# Contributing / collaborating on this project

This repo has one owner and invited collaborators.

## Ground rules

- **Never commit secrets.** No LiveKit API keys, tokens, `.env` files, customer
  phone numbers or call logs. The repo is public; treat every commit as published.
- **Work in branches or a fork.** Open a pull request into `main`; the owner reviews
  and merges.
- **Deploys are owner-only.** Only code merged into `main` gets deployed to the
  owner's LiveKit Cloud project. Free plan = one agent, so experiment deploys do NOT
  go to the owner's project.
- To run your own build: create your own free LiveKit Cloud project, copy
  `livekit.toml.example`, fill in your credentials, and `lk agent deploy .` from
  your branch. Your demo link comes from your own project.

## Repo layout

- `agent.py` — the receptionist agent (config-driven, reads `business.yaml`)
- `business.yaml` — active business pack (name, services, hours, language style)
- `packs/` — ready-made packs (`laundry.yaml` = Tumbledry-style, `salon.yaml` = salon demo)
- `demo_data.json` — fake orders/slots for demo calls; replace with real integrations
- `requirements.txt` — Python deps (LiveKit Agents stack)

## Changing behavior

- New business vertical → add `packs/<name>.yaml`, don't hardcode in `agent.py`
- Greeting / language register → edit the pack's `greeting` and `style` fields
- Test by calling your own demo link before opening a PR

## Questions

Open a GitHub issue or ask in the PR thread.
