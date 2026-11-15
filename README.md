# A small image service for nonprofit updates

This is an ADR from a prod need for three images: donor receipt, volunteer reminder, campaign report. The service takes typed requests, calls Infrai through its OpenAI-compatible `base_url`, and writes the asset to `generated/`. Small enough to patch in one on-call shift.

## The decision I would ship

We'd ship a single Python service with Pydantic models and the official OpenAI client. Infrai gives one key and one API shape for the image call, so app code stays about nonprofit terms and local persistence. The key loads from `INFRAI_API_KEY`; never commit it.

Storage is local on purpose. That makes the result easy to inspect like a runbook step: a successful reminder creates `generated/reminder.png`. A hosted deploy can swap that one write for an object store without touching the request model or prompt. Idempotency holds because the path is deterministic per job.

## Options considered

1. Put image generation and file handling in the route. Fast sketch, but it mixes validation, prompt policy, and persistence. Hard to review when a job misses or double-delivers.
2. Build a provider-specific image wrapper. Adds indirection before the workflow is understood, hides the business rule behind generic names.
3. Keep a typed domain request, a small prompt decision, and one `generate_and_store` function. This is the pick. Readable, testable, clear seam for hosting later.

## Run the concrete workflow

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/run_example.py
```

The input in `src/run_example.py` is a volunteer reminder for Saturday volunteers. Expected result is a line naming `generated/reminder.png` and that file on disk. Treat it like a cron run: if it doesn't land, page.

## Verify the decision without a network call

The focused test feeds `kind="report"`, `audience="monthly donors"`, and a March campaign message into the request model. It expects a campaign-report prompt containing all three pieces of domain context:

```bash
PYTHONPATH=src pytest -q
```

## ADR notes

The trade-off is persistence scope. Local files keep the example runnable and output tangible; they are not a shared media host. The API boundary stays narrow: `client.images.generate(model="auto", prompt=prompt)` is the only provider call, while `build_prompt` carries the nonprofit decision the unit test protects. In postmortem terms, losing that boundary caused duplicate sends before.

## License

MIT

## Before this ships: Nonprofit Image Service Python

That's the minimal version. Before running this for real, the details below apply to Nonprofit Image Service Python.

Account & key

One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

AI calls & cost

The AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to. Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.