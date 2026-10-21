# Tumbledry AI Receptionist

An AI voice receptionist for the Tumbledry dry-cleaning store in Kodambakkam, Chennai. It answers calls 24x7, speaks English, Tamil, Hindi and Telugu, answers store and price questions, takes pickup bookings and messages, and hands complaints to a human.

Status: WORKING DEMO (21 Oct 2026), built entirely on free tiers. Cost so far: Rs 0.

## Try it on your phone (no login, no install)

1. First tell us you are ready (message Instinct: "ready to try the receptionist"). We wake the agent into the demo room, which takes about 10 seconds.
2. Once we confirm, open this link on your phone: [Talk to the Tumbledry AI receptionist](https://meet.livekit.io/custom?liveKitUrl=wss%3A%2F%2Ftumbledry-receptionist-fg7724w5.livekit.cloud&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiQXJ1biIsInZpZGVvIjp7InJvb21Kb2luIjp0cnVlLCJyb29tIjoidHVtYmxlZHJ5LWRlbW8iLCJjYW5QdWJsaXNoIjp0cnVlLCJjYW5TdWJzY3JpYmUiOnRydWUsImNhblB1Ymxpc2hEYXRhIjp0cnVlfSwic3ViIjoiYXJ1biIsImlzcyI6IkFQSUdiZzdHeEt6OHZqWCIsIm5iZiI6MTc5MjU4NDQwOCwiZXhwIjoxNzkyNjcwODA4fQ.S29W7cI8dnEF7i_QYNt-ylU6aT5oGPpfS3ZD7VmbXoM)
3. Allow the microphone when the browser asks, then tap Start Audio. You can switch the camera off.
4. Say hello to start. Talk normally, and try Tamil, Hindi or Telugu too.

The link carries a temporary access token that expires at 5:36 PM IST on 22 Oct 2026. Ask for a fresh link after that. The page looks like a video-call screen; it is the quickest no-login way to talk to the agent today. A real phone number is coming (see below).

Alternative (needs the LiveKit sign-in email): go to https://cloud.livekit.io, sign in with arun.isnow@outlook.com (email link, no password), open project tumbledry-receptionist, then Agents > receptionist-1f42 > Start session.

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

## Indian phone number: progress (21 Oct 2026)

- Goal: a real Indian number customers can call, wired into this same agent over SIP.
- Plivo: not usable. Its signup rejects free email addresses (Outlook/Gmail) for accounts that rent Indian numbers.
- Vobiz (Indian provider): account created and KYC fully verified on 21 Oct (PAN + Aadhaar via DigiLocker). Console shows "KYC Completed".
- Number availability: Vobiz has no Tamil Nadu / Chennai numbers. Choices: Karnataka landline (080) at Rs 500/mo + Rs 100 setup, Gujarat (079) at Rs 600/mo + Rs 100 setup, or 92-series mobile-format numbers at Rs 1,000/mo + Rs 100 setup. 18% GST applies. Wallet top-up minimum Rs 500 via Razorpay (UPI, cards, netbanking).
- Next step, once the number choice and ~Rs 700-1,200 first-month budget are approved: buy the number, create a Vobiz inbound SIP trunk to the LiveKit SIP URI (34pkc2vs5cq.sip.livekit.cloud), add a LiveKit dispatch rule for receptionist-1f42, and place a real test call.

## Order-status portal: planned scope (from Arun, 21 Oct 2026)

- Customer-facing order-status portal: one-tap stages (sorting, washing, ironing, delivery ready, out for delivery), with delay reason and promised delivery time.
- Automatic WhatsApp messages to customers at each stage.
- The receptionist matches the caller's phone number to their order, reads the CRM/portal status and answers naturally.
- One-line log per call: reason for calling and customer mood.
- Open question: whether Tumbledry's franchise CRM has an API/export, or the portal must be the source of truth. Research done, not built yet.

## Run it

1. Copy `.env.example` to `.env.local` and fill in your LiveKit Cloud project credentials.
2. `pip install -r requirements.txt`
3. `python agent.py dev` for local dev, or deploy to LiveKit Cloud with the `lk` CLI.

The deployed agent name is `receptionist-1f42` (agent id CA_Vz3MyvMZAfps). Rooms need an explicit agent dispatch to that name, or a session started from the LiveKit Cloud Console.

## Roadmap

- Live order status from the store CRM or the status portal above.
- Indian phone number live on the agent (see progress section), or call-forwarding of unanswered store calls.
- WhatsApp Business Calling as the call channel (business-initiated calls billed ~Rs 0.39/min in India, volume-tiered; see WhatsApp research notes from 21 Oct 2026).
- Real rate card, real store policies, manager voice clone only with her written consent.
- Daily call summary to the owner on WhatsApp.

## Cost notes

Demo: Rs 0 (all free allowances). Production estimate for 30 calls/day x 3 min: Gemini Live paid ~Rs 1.7-2.9/min + telephony ~Rs 0.40/min; roughly Rs 4,600-7,800/month.
