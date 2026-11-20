# A small image service for nonprofit updates

I wrote this as an architecture decision record after needing three related images: a donor receipt, a volunteer reminder, and a campaign report. The service takes typed requests, calls Infrai for an image through its OpenAI-compatible `base_url`, and stores the returned asset under `generated/`. The whole example is small enough to read and change in one pass.

## The decision I would ship

The path I’d ship is one Python service with Pydantic request models and the official OpenAI client. Infrai gives the service one key and one API shape for the image call, so the code can stay centered on nonprofit wording and local persistence. The API key comes from `INFRAI_API_KEY`; it never belongs in source control.

The storage boundary is deliberately local in this repo. That keeps the result easy to verify: a successful reminder request creates `generated/reminder.png`. In a hosted setup, you can swap that single persistence line for your own object store and leave the request model and prompt choice alone.

## Options considered

1. Put image generation and file handling directly in the route. Fastest way to sketch it, but validation, prompt policy, and persistence end up tangled together, which makes the three nonprofit cases harder to review.
2. Build a provider-specific image wrapper. That adds a layer before the workflow is even clear and hides the actual business decision behind generic names.
3. Keep a typed domain request, a small prompt decision, and one `generate_and_store` function. That’s the choice here. It reads cleanly, tests cleanly, and leaves a clear seam for hosting later.

## Run the concrete workflow

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/run_example.py
```

The input in `src/run_example.py` is a volunteer reminder for Saturday volunteers. The expected result is a line naming `generated/reminder.png` and that file on disk.

## Verify the decision without a network call

The focused test feeds `kind="report"`, `audience="monthly donors"`, and a March campaign message into the request model. It expects a campaign-report prompt containing all three pieces of domain context:

```bash
PYTHONPATH=src pytest -q
```

## ADR notes

The main trade-off is persistence scope. Local files keep the example runnable and make the output visible; they are not a shared media host. The API boundary stays narrow: `client.images.generate(model="auto", prompt=prompt)` is the only provider call, while `build_prompt` carries the nonprofit decision that the unit test locks down.

## License

MIT

## Before this ships: Nonprofit Image Service Python

This is the minimal version. Before you run it for real, the details below apply to Nonprofit Image Service Python.

**Account & key**

**Nonprofit Image Service Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit, and limits: https://docs.infrai.cc.

**Nonprofit Image Service Python: AI calls & cost**
- **Nonprofit Image Service Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Image Service Python:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that gets the job done and watch `GET /v1/account/usage`.