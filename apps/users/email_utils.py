"""
Email confirmation helpers — delivery via Supabase Auth OTP API.

No SMTP credentials needed.  Only requires:
    SUPABASE_URL  = https://<project-ref>.supabase.co
    SUPABASE_ANON_KEY = <anon / public key>

Flow:
  1. We generate a signed token (Django signing) that encodes the user PK.
  2. We call  POST /auth/v1/otp  on the Supabase project.
     Supabase sends a "magic-link" email from their own infrastructure.
     The magic-link contains a `redirect_to` that points at our Django
     confirm-email endpoint, with our signed token as a query param.
  3. The user clicks the link → Supabase verifies their side → redirects
     to  GET /api/auth/confirm-email/?token=<our_token>
  4. Our endpoint verifies the signed token and marks is_email_verified=True.
"""
import logging
from urllib.parse import quote

import httpx
from django.conf import settings
from django.core import signing

logger = logging.getLogger(__name__)

TOKEN_MAX_AGE_SECONDS = 24 * 60 * 60   # 24 hours
_SALT = "petso-email-confirmation-v1"


# ── Token helpers ────────────────────────────────────────────────────────────

def make_confirmation_token(user_pk: int) -> str:
    """Return a URL-safe signed token that encodes *user_pk*."""
    return signing.dumps(user_pk, salt=_SALT)


def verify_confirmation_token(token: str) -> int:
    """
    Decode and verify *token*.  Returns the user PK (int) on success.
    Raises signing.SignatureExpired or signing.BadSignature on failure.
    """
    return signing.loads(token, salt=_SALT, max_age=TOKEN_MAX_AGE_SECONDS)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _public_base_url() -> str:
    url = getattr(settings, "PETSO_PUBLIC_BASE_URL", "").strip().rstrip("/")
    return url or "http://95.216.63.81:8000"


def _supabase_url() -> str:
    return getattr(settings, "SUPABASE_URL", "").strip().rstrip("/")


def _supabase_anon_key() -> str:
    return getattr(settings, "SUPABASE_ANON_KEY", "").strip()


# ── Email sending ─────────────────────────────────────────────────────────────

def send_confirmation_email(user) -> bool:
    """
    Send a confirmation email to *user* via Supabase OTP / magic-link.

    Supabase delivers the email from their own infrastructure — no SMTP
    configuration is required.  The magic-link `redirect_to` carries our
    signed token so Django can verify independently.

    Returns True on success, False on any error (logged).
    """
    supabase_url = _supabase_url()
    anon_key = _supabase_anon_key()

    if not supabase_url or not anon_key:
        logger.error(
            "SUPABASE_URL or SUPABASE_ANON_KEY not set — cannot send confirmation email."
        )
        return False

    token = make_confirmation_token(user.pk)
    # Put the token in the URL *path* (not a query param) so Supabase's
    # redirect-URL wildcard  /api/auth/confirm-email/*  matches it exactly
    # and the token is not mangled by double-encoding of query strings.
    token_encoded = quote(token, safe='')
    redirect_to = f"{_public_base_url()}/api/auth/confirm-email/{token_encoded}/"

    try:
        resp = httpx.post(
            f"{supabase_url}/auth/v1/otp",
            headers={
                "apikey": anon_key,
                "Content-Type": "application/json",
            },
            json={
                "email": user.email,
                "create_user": True,          # create in Supabase auth only for email delivery
                "options": {
                    "emailRedirectTo": redirect_to,
                },
            },
            timeout=10,
        )

        if resp.status_code == 200:
            logger.info("Confirmation email sent to %s via Supabase OTP.", user.email)
            return True

        logger.error(
            "Supabase OTP failed for %s — status %s: %s",
            user.email, resp.status_code, resp.text,
        )
        return False

    except Exception as exc:
        logger.error("Error calling Supabase OTP for %s: %s", user.email, exc)
        return False
