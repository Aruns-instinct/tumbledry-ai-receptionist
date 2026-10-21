"""SMB AI Receptionist - config-driven voice agent.
One codebase, any business. Config comes from the embedded defaults below and is
overridden by business.yaml + packs/<pack>.yaml when those files exist (CLI deploy).
Data backend: Google Sheet when sheet_id + GOOGLE_SERVICE_ACCOUNT_JSON are set,
otherwise demo mode with embedded sample data (zero setup).
"""
import json, logging, os, datetime, re
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli, inference, room_io, function_tool, RunContext

logger = logging.getLogger("agent-receptionist-smb")
load_dotenv(".env.local")

BASE = Path(__file__).parent

# ---- embedded defaults (Tumbledry = pack #1; a new business overrides via files or edits) ----
DEFAULT_BIZ = {
    "business_id": "tumbledry-kodambakkam",
    "pack": "laundry",
    "name": "Tumbledry",
    "area": "Kodambakkam, Chennai",
    "greeting": "Vanakkam! Thank you for calling Tumbledry Kodambakkam. I am the store's AI assistant. How can I help you today?",
    "hours": "9 AM to 9 PM every day",
    "languages": ["english", "tamil", "hindi", "telugu"],
    "default_language": "english",
    "manager": {"name": "the store manager", "callback_promise": "the same day"},
    "sheet_id": "",
    "services": ["dry cleaning", "wash and iron", "wash and fold", "ironing", "shoe and bag cleaning", "sofa and carpet cleaning"],
    "prices": ["shirt wash and iron Rs 99", "saree dry clean from Rs 299", "suit dry clean from Rs 499", "bedsheet Rs 199", "shoes from Rs 349"],
    "pickup": {"free": True, "slot_hours": [9, 21], "slot_len_hours": 2},
}
DEFAULT_PACKS = {
    "laundry": {
        "booking_noun": "pickup",
        "status_stages": ["received", "sorting", "washing", "ironing", "delivery ready", "out for delivery", "delivered"],
        "faq_seeds": ("Stain questions: ask what the garment is and what caused the stain, then say the store "
                      "team will examine it and confirm on WhatsApp - never promise stain removal. "
                      "Saree fall/pico, blazer, suit, shoes, sofa and carpet cleaning are normal services. "
                      "Delivery time: normal 2 days, express next day (team confirms)."),
    },
}
DEFAULT_DEMO = {
    "orders": [
        {"phone": "9000000001", "name": "Kavya", "order": "TD-1042", "items": "2 sarees dry clean", "stage": "ironing", "ready": "Thursday evening"},
        {"phone": "9000000002", "name": "Ramesh", "order": "TD-1043", "items": "1 suit dry clean", "stage": "delivery ready", "ready": "today"},
        {"phone": "9000000003", "name": "Meena", "order": "TD-1044", "items": "shoes cleaning", "stage": "washing", "ready": "Friday"},
    ],
    "bookings": [],
    "calls": [],
}

def _deep(default, override):
    out = dict(default)
    for k, v in (override or {}).items():
        out[k] = _deep(default.get(k, {}), v) if isinstance(v, dict) and isinstance(default.get(k), dict) else v
    return out

def load_config():
    biz, packs, demo = DEFAULT_BIZ, DEFAULT_PACKS, DEFAULT_DEMO
    try:
        import yaml
        bf = BASE / "business.yaml"
        if bf.exists():
            biz = _deep(DEFAULT_BIZ, yaml.safe_load(bf.read_text()) or {})
        pf = BASE / "packs" / f"{biz.get('pack','laundry')}.yaml"
        packs = dict(DEFAULT_PACKS)
        if pf.exists():
            packs[biz.get("pack", "laundry")] = _deep(DEFAULT_PACKS.get(biz.get("pack", "laundry"), {}), yaml.safe_load(pf.read_text()) or {})
        df = BASE / "demo_data.json"
        if df.exists():
            demo = json.loads(df.read_text())
    except Exception as e:
        logger.warning("file config skipped: %s", e)
    return biz, packs.get(biz.get("pack", "laundry"), {}), demo

BIZ, PACK, DEMO = load_config()

# ---------- data backend ----------
class Store:
    """Google Sheet when configured, else embedded demo data. Same methods either way."""
    def __init__(self):
        self.sheet_id = BIZ.get("sheet_id") or ""
        self._sa = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        self.live = bool(self.sheet_id and self._sa)
        if self.live:
            try:
                from google.oauth2 import service_account
                info = json.loads(self._sa)
                self._creds = service_account.Credentials.from_service_account_info(
                    info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
                logger.info("Store: LIVE Google Sheet %s", self.sheet_id)
            except Exception as e:
                logger.error("Sheet auth failed, falling back to demo: %s", e)
                self.live = False
        if not self.live:
            logger.info("Store: DEMO mode (%d sample orders)", len(DEMO["orders"]))

    def _token(self):
        import google.auth.transport.requests
        self._creds.refresh(google.auth.transport.requests.Request())
        return self._creds.token

    def _sheets(self, method, path, body=None):
        import urllib.request
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}{path}"
        req = urllib.request.Request(url, method=method,
            data=json.dumps(body).encode() if body else None,
            headers={"Authorization": f"Bearer {self._token()}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())

    def _read_tab(self, tab):
        if not self.live:
            return DEMO.get(tab, [])
        res = self._sheets("GET", f"/values/{tab}!A:Z")
        rows = res.get("values", [])
        if not rows:
            return []
        hdr = rows[0]
        return [dict(zip(hdr, r + [""] * (len(hdr) - len(r)))) for r in rows[1:]]

    def _append_tab(self, tab, rec):
        if not self.live:
            DEMO.setdefault(tab, []).append(rec)
            return
        hdr = self._sheets("GET", f"/values/{tab}!A1:Z1").get("values", [[]])[0]
        row = [str(rec.get(h, "")) for h in hdr]
        self._sheets("POST", f"/values/{tab}!A1:append?valueInputOption=RAW", {"values": [row]})

    def find_orders(self, phone):
        digits = re.sub(r"\D", "", str(phone))[-10:]
        return [o for o in self._read_tab("orders") if digits and re.sub(r"\D", "", str(o.get("phone", "")))[-10:] == digits]

    def booked_slots(self, day):
        return [b.get("slot", "") for b in self._read_tab("bookings") if b.get("date") == day]

    def add_booking(self, rec):
        self._append_tab("bookings", rec)

    def add_call(self, rec):
        self._append_tab("calls", rec)

STORE = Store()

def slots_for(day_str):
    """Free pickup slots for a YYYY-MM-DD."""
    try:
        datetime.date.fromisoformat(day_str)
    except (ValueError, TypeError):
        return []
    start, end = BIZ.get("pickup", {}).get("slot_hours", [9, 21])
    ln = BIZ.get("pickup", {}).get("slot_len_hours", 2)
    taken = set(STORE.booked_slots(day_str))
    out, h = [], start
    while h + ln <= end:
        s = f"{h:02d}:00-{h+ln:02d}:00"
        if s not in taken:
            out.append(s)
        h += ln
    return out

def build_instructions():
    langs = ", ".join(str(x) for x in BIZ.get("languages", ["english"])).title()
    prices = "; ".join(str(x) for x in BIZ.get("prices", []))
    services = ", ".join(str(x) for x in BIZ.get("services", []))
    noun = PACK.get("booking_noun", "pickup")
    faq = PACK.get("faq_seeds", "")
    stages = ", ".join(str(x) for x in PACK.get("status_stages", []))
    mgr = BIZ.get("manager", {})
    return f"""You are the friendly AI receptionist of {BIZ.get('name')}, a business in {BIZ.get('area')}, India. Always identify yourself as the business's AI assistant if anyone asks.

LANGUAGE: Start in {str(BIZ.get('default_language', 'english')).title()}. If the caller speaks {langs}, switch to their language and continue in it.

TAMIL STYLE (very important): Speak normal, relaxed Chennai spoken Tamil (pechu vazhakku), casual but polite. NEVER use formal, literary or news-style Tamil. Talk like a friendly person at a real Chennai shop counter. Mix common English words naturally, exactly the way Chennai people speak every day: order, pickup, delivery, timing, price, WhatsApp, booking. Examples of your Tamil:
- "Sollunga, epdi help pannattum?"
- "Daily morning 9 to night 9 open dhaan."
- "Unga peru, phone number sollunga."
Use everyday forms like "dhaan", "pannidunga", "sollunga", "romba thanks". Never sound like a newsreader or a formal letter (no "mikka nandri", "evvaaru").
HINDI STYLE: natural everyday spoken Hindi, polite but relaxed, mixing English words like a real shop would. Not textbook Hindi.
TELUGU STYLE: natural everyday spoken Telugu, polite but relaxed, mixing English words the same way.

FACTS: Open {BIZ.get('hours')}. Located in {BIZ.get('area')}. Services: {services}. {'Free home pickup and delivery.' if BIZ.get('pickup', {}).get('free') else ''}
PRICES (approximate; offer to confirm exact rates on WhatsApp): {prices}. For anything not listed, say the team will confirm the exact price on WhatsApp.

ORDER STATUS (use the lookup_order tool): when a caller asks about an order, ask their phone number (the one given at the store) and call lookup_order. If found, tell them the stage naturally (stages flow: {stages}) and the ready time. If not found, take name, phone and order number and promise the team will WhatsApp the status.

BOOKING (use the tools): when a caller wants a {noun}, ask which day, call get_slots for that day, offer two or three options, then collect name, phone number, address and call book_slot. After a successful booking, tell them a WhatsApp confirmation will follow.

ESCALATION (use the escalate tool): for complaints, listen fully, apologize once, then call escalate with a one-line summary and promise a callback from {mgr.get('name', 'the manager')} {mgr.get('callback_promise', 'the same day')}. Also escalate if the caller insists on talking to the owner or manager.

CALL LOG (required): before ending EVERY call, call log_call with the reason (one line), the caller's mood, and the outcome.

KNOWLEDGE: {faq}

STYLE: Warm and professional, but in every language sound like a friendly local person, not a call-center script. Keep answers to one or two sentences. Ask one question at a time. Never invent prices, timings or order details - use the tools or say the team will call back. This is a demo build, so if asked, you may say you are a trial version."""

class SMBAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=build_instructions())

    async def on_enter(self):
        await self.session.generate_reply(
            instructions='Greet the caller with exactly this line, warmly and naturally: "'
                + BIZ.get("greeting", "Hello! How can I help you today?") + '"',
            allow_interruptions=True)

    @function_tool
    async def lookup_order(self, ctx: RunContext, phone: str) -> str:
        """Look up orders for a customer phone number. Returns order stages and ready times."""
        found = STORE.find_orders(phone)
        if not found:
            return f"No order found for phone number {phone}."
        return "; ".join(f"{o.get('order')}: {o.get('items')} - stage '{o.get('stage')}', ready {o.get('ready')}" for o in found)

    @function_tool
    async def get_slots(self, ctx: RunContext, date: str) -> str:
        """Get free pickup slots for a date in YYYY-MM-DD format."""
        free = slots_for(date)
        if not free:
            return f"No free slots on {date}. Suggest another day."
        return f"Free slots on {date}: " + ", ".join(free)

    @function_tool
    async def book_slot(self, ctx: RunContext, name: str, phone: str, address: str, date: str, slot: str) -> str:
        """Book a pickup slot after the caller confirms name, phone, address, date and slot."""
        if slot not in slots_for(date):
            return f"Slot {slot} on {date} is not available. Offer: " + ", ".join(slots_for(date)[:3])
        noun = PACK.get("booking_noun", "pickup")
        rec = {"name": name, "phone": phone, "address": address, "date": date, "slot": slot,
               "booked_at": datetime.datetime.now().isoformat(timespec="seconds")}
        STORE.add_booking(rec)
        confirmation = f"{BIZ.get('name')} {BIZ.get('area')}: {noun} confirmed for {date}, {slot}. Address: {address}. Questions? Reply here."
        logger.info("BOOKING %s | WhatsApp confirmation text: %s", {k: rec[k] for k in ('name', 'phone', 'date', 'slot')}, confirmation)
        return f"Booked. {noun.title()} on {date} at {slot} for {name}, {address}. A WhatsApp confirmation will follow."

    @function_tool
    async def escalate(self, ctx: RunContext, summary: str) -> str:
        """Escalate to the manager with a one-line context summary. Use for complaints or owner requests."""
        mgr = BIZ.get("manager", {})
        STORE.add_call({"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "reason": "escalation", "mood": "upset", "outcome": summary})
        logger.info("ESCALATION: %s", summary)
        return f"Escalated to {mgr.get('name', 'the manager')} with your summary. Tell the caller the manager will call back {mgr.get('callback_promise', 'the same day')}."

    @function_tool
    async def log_call(self, ctx: RunContext, reason: str, mood: str, outcome: str) -> str:
        """Log this call before it ends. reason: one line. mood: happy/neutral/upset. outcome: what was done."""
        STORE.add_call({"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "reason": reason, "mood": mood, "outcome": outcome})
        logger.info("CALL LOG reason=%s mood=%s outcome=%s", reason, mood, outcome)
        return "Logged."

# Noise cancellation: optional plugin; some environments bundle it, others don't.
def audio_input_options():
    try:
        from livekit.plugins import ai_coustics
        return room_io.AudioInputOptions(
            noise_cancellation=ai_coustics.audio_enhancement(
                model=ai_coustics.EnhancerModel.QUAIL_VF_S))
    except Exception as e:
        logger.warning("noise cancellation unavailable: %s", e)
        return room_io.AudioInputOptions()

server = AgentServer()

@server.rtc_session(agent_name="receptionist-1f42")
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        llm=inference.RealtimeModel(model="google/gemini-3.8-live", voice="Kore"),
    )
    await session.start(
        agent=SMBAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(audio_input=audio_input_options()),
    )

if __name__ == "__main__":
    cli.run_app(server)
