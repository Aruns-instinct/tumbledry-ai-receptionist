# Contributing / collaborating on this project

This repo has one owner and invited collaborators.

## Ground rules

- **Never commit secrets.** No LiveKit API keys, tokens, service-account JSON, or
  customer data. Config goes in `business.yaml`; credentials stay in environment
  variables / agent secrets. If a secret ever lands in a commit, treat it as
  compromised and rotate it.
- **`main` is the deployed demo.** What is on `main` is what the live receptionist
  runs. Do not push experiment code directly to `main`.
- **Work in branches or a fork.** Open a pull request into `main`; the owner reviews
  and merges. One PR = one change you can describe in a sentence.

## Two ways to collaborate

1. **Fork (default, safest).** Fork this repo to your own GitHub account, change
   anything, open a PR back. No access grants needed; your fork is your sandbox.
2. **Collaborator (if invited).** You get write access. Still work on a branch and
   open PRs - `main` is protected.

## Builds

- The live demo deploys from `main` only, via `lk agent deploy .` (see README), to the
  owner's LiveKit Cloud project. Free plan = one agent, so experiment deploys do NOT
  go to the owner's project.
- For your own test builds: create a free LiveKit Cloud account, `lk agent create .`
  in your clone, and you get your own demo link. Your builds stay yours; the shared
  demo updates only after a merge to `main`.

## Repo map

- `agent.py` - the agent (config-driven; behavior comes from config, not code edits)
- `business.yaml` - the business being served (Tumbledry today)
- `packs/*.yaml` - industry packs (laundry, salon)
- `demo_data.json` - sample data for demo mode
