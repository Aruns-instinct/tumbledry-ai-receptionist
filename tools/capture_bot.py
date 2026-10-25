import asyncio, sys, datetime, json
from livekit import rtc, api

KEY=open("/home/sandbox/.lk/key").read().strip(); SECRET=open("/home/sandbox/.lk/secret").read().strip()
ROOM=sys.argv[1]; OUT=sys.argv[2]; MINUTES=int(sys.argv[3]) if len(sys.argv)>3 else 30
wss="wss://tumbledry-receptionist-fg7724w5.livekit.cloud"
tok=(api.AccessToken(KEY,SECRET).with_identity("capture-bot").with_name("capture")
    .with_grants(api.VideoGrants(room_join=True, room=ROOM, hidden=True))
    .with_kind("agent")
    .with_ttl(datetime.timedelta(minutes=MINUTES+5)).to_jwt())
finals = {}  # segment_id -> {track, text}
track_owner = {}

async def main():
    room = rtc.Room()
    def handler(reader, participant_identity):
        async def consume():
            attrs = dict(reader.info.attributes or {})
            text = await reader.read_all()
            if attrs.get("lk.transcription_final") == "true":
                sid = attrs.get("lk.segment_id", reader.info.stream_id)
                tid = attrs.get("lk.transcribed_track_id", "")
                if sid not in finals:
                    finals[sid] = {"track": tid, "text": text.strip()}
                    line = f"[{track_owner.get(tid, tid or '?')}] {text.strip()}"
                    print(line, flush=True)
                    with open(OUT, "a") as f:
                        f.write(line + "\n")
        asyncio.create_task(consume())
    room.register_text_stream_handler("lk.transcription", handler)

    @room.on("track_published")
    def _tp(pub, participant):
        track_owner[pub.sid] = participant.identity
    @room.on("participant_connected")
    def _pc(participant):
        for t in participant.track_publications.values():
            track_owner[t.sid] = participant.identity
    await room.connect(wss, tok)
    for p in room.remote_participants.values():
        for t in p.track_publications.values():
            track_owner[t.sid] = p.identity
    print("capture bot connected", flush=True)
    await asyncio.sleep(MINUTES*60)
    await room.disconnect()

asyncio.run(main())
