# Tumbledry AI Receptionist

An AI voice receptionist for the Tumbledry dry-cleaning store in Kodambakkam, Chennai. It answers calls 24x7, speaks English, Tamil, Hindi and Telugu, answers store and price questions, takes pickup bookings and messages, and hands complaints to a human.

Status: WORKING DEMO (21 Oct 2026), built entirely on free tiers. Cost so far: Rs 0.

## Stack

- LiveKit Cloud, free Build plan: agent hosting (1,000 agent minutes/month free), WebRTC transport.
- LiveKit Agents SDK (open source, Apache-2.0): agent framework.
- Google Gemini 3.8 Live (realtime speech-to-speech) via LiveKit Inference: free $2.50/month credit covers ~170 call minutes.
- Voice: Kore (female, multilingual automatic).

## What it does today

- Greets callers: "Vanakkam! Thank you for calling Tumbledry Kodambakkam..."
- Answers store hours (9 AM - 9 PM daily), location, services and indicative prices (shirt Rs 99, saree from Rs 299, suit from Rs 499, bedsheet Rs 199, shoes from Rs 349).
- Takes order-status requests as a callback (name, phone, order number) - no live CRM link yet.
- Takes pickup bookings and complaints as messages for the store team.
- Switches language to match the caller (English, Tamil, Hindi, Telugu).

## Validated demo session (21 Oct 2026)

- Agent: "Vanakkam! Thank you for calling Tumbledry Kodambakkam. I am the store's AI assistant. How can I help you today?"
- Caller: "What are your store timings?" -> Agent: "We are open from 9 AM to 9 PM every single day."
- Caller: "How much to dry clean a saree?" -> Agent: "Saree dry cleaning starts from Rs 299. I can have our team confirm the exact rate for your specific saree on WhatsApp."

## Run it

1. Copy `.env.example` to `.env.local` and fill in your LiveKit Cloud project credentials.
2. `pip install -r requirements.txt`
3. `python agent.py dev` for local dev, or deploy to LiveKit Cloud with the `lk` CLI.

The deployed agent name is `receptionist-1f42` (agent id CA_Vz3MyvMZAfps). Rooms need an explicit agent dispatch to that name, or a session started from the LiveKit Cloud Console.

## Roadmap

- Live order status from the store CRM (or a staff-updated sheet until then).
- Indian phone number via Plivo/Vobiz with SIP trunk into LiveKit (~Rs 0.40/min + number rental), or call-forwarding of unanswered store calls.
- WhatsApp Business Calling as the call channel (business-initiated calls billed ~Rs 0.39/min in India, volume-tiered; see WhatsApp research notes from 21 Oct 2026).
- Real rate card, real store policies, manager voice clone only with her written consent.
- Daily call summary to the owner on WhatsApp.

## Cost notes

Demo: Rs 0 (all free allowances). Production estimate for 30 calls/day x 3 min: Gemini Live paid ~Rs 1.7-2.9/min + telephony ~Rs 0.40/min; roughly Rs 4,600-7,800/month.
