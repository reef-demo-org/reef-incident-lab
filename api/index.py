"""Reef three-wave incident lab — FastAPI on Vercel.

Wave behavior is controlled by DEPLOY_WAVE (set in Vercel Production env):
  1 — baseline: /health, /checkout, /auth/login all succeed
  2 — checkout TypeError (Sentry error class A)
  3 — auth 401 + Sentry capture; checkout fixed again
"""

from __future__ import annotations

import os
from typing import Any

import sentry_sdk
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=1.0,
    )

WAVE = int(os.environ.get("DEPLOY_WAVE", "1"))

app = FastAPI(
    title="Reef Incident Lab API",
    version="0.1.0",
    description="Intentional regressions for Reef/Coral demo waves.",
)


class CheckoutRequest(BaseModel):
    cart_id: str | None = None
    amount: float | None = None


class LoginRequest(BaseModel):
    email: str = Field(..., examples=["user@demo.com"])
    password: str = Field(..., examples=["demo-password"])


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "wave": WAVE}


@app.get("/deploy-info")
def deploy_info() -> dict[str, Any]:
    return {
        "deploy_wave": WAVE,
        "sentry_configured": bool(SENTRY_DSN),
        "environment": os.environ.get("SENTRY_ENVIRONMENT", "production"),
    }


@app.post("/checkout")
def checkout(body: CheckoutRequest) -> dict[str, Any]:
    if WAVE == 2:
        amount = body.amount
        total = amount + 10  # TypeError when amount is None (wave 2 demo)
        return {"total": total, "cart_id": body.cart_id}

    total = 99.0 if body.amount is None else float(body.amount) + 10
    return {"total": total, "cart_id": body.cart_id, "status": "ok"}


@app.post("/auth/login")
def login(body: LoginRequest) -> dict[str, str]:
    if WAVE == 3:
        sentry_sdk.capture_exception(ValueError("invalid credentials schema"))
        raise HTTPException(status_code=401, detail="invalid credentials")

    return {"token": "demo-token-ok", "email": body.email}
