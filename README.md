# SMB AI Receptionist

A voice AI receptionist that works for any small or medium business. One codebase:
each business is a config file (`business.yaml`) plus an industry pack (`packs/*.yaml`).
The first reference business is Tumbledry, Kodambakkam, Chennai (pack: `laundry`).

Built on the free stack: LiveKit Agents + LiveKit Cloud (Build plan) + Gemini Live via
LiveKit Inference. No paid services required to run the demo.

## What it does on a call

- Greets the caller as the business's AI assistant, in English, Tamil, Hindi or Telugu
  (Chennai spoken-Tamil register, natural Tanglish mixing).
- Answers hours, location, services and prices from the business config.
- **Order status lookup**: caller gives their phone number, the agent looks up their
  order and reads out the stage and ready time (`lookup_order` tool).
- **Pickup/appointment booking**: offers real free slots, books with name, phone and
  address, and generates the WhatsApp confirmation text (`get_slots`, `book_slot`).
  Double-booked slots are rejected automatically. Bookings create a Google Calendar
  event when `calendar_id` + a service account are configured (demo mode otherwise).
- **Human handoff with context**: complaints or owner requests are escalated to the
  manager with a one-line summary (`escalate`).
- **CRM-style call log**: every call ends with a structured log of reason, caller mood
  and outcome (`log_call`).

## Data backend: demo mode vs live mode

- **Demo mode (default)**: works out of the box with sample data in `demo_data.json`.
  Nothing to connect.
- **Live mode**: set `sheet_id` in `business.yaml` to a Google Sheet with tabs
  `orders`, `bookings`, `calls` (first row = column headers), and set the
  `GOOGLE_SERVICE_ACCOUNT_JSON` agent secret (a service account the sheet is shared
  with). The same tools then read and write the sheet.

## Onboard a new business (self-serve)

1. Copy `business.yaml`, edit name, area, hours, services, prices, manager, languages.
2. Pick the closest pack in `packs/` (`laundry`, `salon`) or copy one to a new pack with
   your booking noun (`pickup`, `appointment`, `table`), status stages and FAQ seeds.
   See `business-salon.example.yaml` for a salon setup (1-hour appointment slots).
3. Replace `demo_data.json` samples, or point `sheet_id` at the business's Google Sheet.
4. Deploy (see below). The agent name, greeting and behavior all come from config.

## Deploy to LiveKit Cloud

```
pip install livekit-cli   # or: curl -sSL https://get.livekit.io/cli | bash
export LIVEKIT_URL=wss://<your-project>.livekit.cloud
export LIVEKIT_API_KEY=... LIVEKIT_API_SECRET=...
lk agent create .          # first time
lk agent deploy .          # subsequent versions (agent id lives in livekit.toml)
```

The deployed worker registers as dispatch name `receptionist-1f42`. Create a room and
dispatch the agent per session (it is not 24x7 in a room):

```python
await lk.room.create_room(api.CreateRoomRequest(name="demo", empty_timeout=600))
await lk.agent_dispatch.create_dispatch(api.CreateAgentDispatchRequest(
    room="demo", agent_name="receptionist-1f42"))
```

Join link for a human: `https://meet.livekit.io/custom?liveKitUrl=<url-encoded-wss>&token=<jwt>`.

## Repo layout

- `agent.py` - the whole agent: config loader, sheet/demo backend, tools, instructions builder
- `business.yaml` - per-business config (Tumbledry = reference)
- `packs/laundry.yaml` - industry pack: booking shape, status stages, FAQ seeds
- `demo_data.json` - sample orders for demo mode
- `requirements.txt`, `Dockerfile`, `.dockerignore`, `livekit.toml` - deployment
- `.env.example` - environment variables (never commit real keys)

## Google Calendar backend

Set `calendar_id` in `business.yaml` (or the `GOOGLE_CALENDAR_ID` secret) plus
`GOOGLE_SERVICE_ACCOUNT_JSON` (a service account the calendar is shared with, Calendar
API enabled). Then `get_slots` reads busy slots from the calendar and `book_slot`
creates the event. Without them, slots and bookings run on the demo/sheet backend.

## Roadmap

- Real WhatsApp sends via WhatsApp Business API (confirmation text is generated and logged today)
- Live call transfer to the manager's phone (needs a phone number / SIP trunk)
- More industry packs: clinic, restaurant, tuition center
