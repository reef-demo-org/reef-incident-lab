# reef-incident-lab

Minimal FastAPI app for the Reef three-wave incident demo. Deployed on Vercel; errors flow to Sentry; Reef/Coral correlate GitHub PRs, deploys, and issues.

See [docs/demo-three-wave.txt](../docs/demo-three-wave.txt) in the main Reef repo for full choreography.

## Endpoints

| Method | Path | Wave 1 | Wave 2 | Wave 3 |
|--------|------|--------|--------|--------|
| GET | `/health` | 200 | 200 | 200 |
| GET | `/deploy-info` | wave env | wave env | wave env |
| POST | `/checkout` | 200 | **TypeError → 500** | 200 (fixed) |
| POST | `/auth/login` | 200 | 200 | **401** |

## Vercel setup

1. Import `reef-demo-org/reef-incident-lab` at [vercel.com/new](https://vercel.com/new).
2. Framework: **Other** (Vercel auto-detects FastAPI from `api/index.py`).
3. Production environment variables:

   ```
   SENTRY_DSN=https://...@....ingest.sentry.io/...
   SENTRY_ENVIRONMENT=production
   DEPLOY_WAVE=1
   ```

4. After each wave merge, update `DEPLOY_WAVE` to `2` then `3` in **Production** and redeploy if needed.

## Smoke tests

```bash
BASE=https://reef-incident-lab.vercel.app   # your production URL

curl -s "$BASE/health"
curl -s "$BASE/deploy-info"

curl -s -X POST "$BASE/checkout" \
  -H "Content-Type: application/json" \
  -d '{"cart_id":"demo-1","amount":null}'

curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@demo.com","password":"wrong"}'
```

Wave 2: repeat checkout curl 10–20 times to populate Sentry.  
Wave 3: repeat login curl; expect 401 and a **new** Sentry issue (distinct from checkout TypeError).

## Local dev

```bash
cd reef-incident-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DEPLOY_WAVE=1
# optional: export SENTRY_DSN=...
uvicorn api.index:app --reload --port 8000
```

## GitHub waves (branches)

| Wave | Branch | Vercel `DEPLOY_WAVE` |
|------|--------|----------------------|
| 1 | `wave-1-baseline` | `1` |
| 2 | `wave-2-checkout-bug` | `2` |
| 3 | `wave-3-auth-bug` | `3` |

Wave logic lives in `api/index.py`; you can switch behavior with env only (no code change) if you prefer.
