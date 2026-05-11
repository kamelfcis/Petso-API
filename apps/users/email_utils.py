"""
Email confirmation helpers.

Token strategy: django.core.signing.dumps / loads
  - Signed with SECRET_KEY + a salt  → tamper-proof
  - Contains a timestamp             → auto-expires after TOKEN_MAX_AGE_SECONDS
  - No DB row needed
"""
import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

TOKEN_MAX_AGE_SECONDS = 24 * 60 * 60   # 24 hours
_SALT = "petso-email-confirmation-v1"


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def make_confirmation_token(user_pk: int) -> str:
    """Return a URL-safe signed token encoding the user PK."""
    return signing.dumps(user_pk, salt=_SALT)


def verify_confirmation_token(token: str) -> int:
    """
    Decode and verify *token*.
    Returns the user PK (int) on success.
    Raises signing.SignatureExpired or signing.BadSignature on failure.
    """
    return signing.loads(token, salt=_SALT, max_age=TOKEN_MAX_AGE_SECONDS)


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------

def _base_url() -> str:
    """Public base URL without trailing slash, e.g. http://95.216.63.81:8000"""
    url = getattr(settings, "PETSO_PUBLIC_BASE_URL", "").strip().rstrip("/")
    return url or "http://95.216.63.81:8000"


def send_confirmation_email(user) -> bool:
    """
    Send an email confirmation link to *user*.
    Returns True on success, False on any SMTP/network error (logged).
    """
    token = make_confirmation_token(user.pk)
    confirm_url = f"{_base_url()}/api/auth/confirm-email/?token={token}"

    subject = "Confirm your Petso account"
    body = (
        f"Hi {user.name},\n\n"
        f"Thanks for registering with Petso!\n\n"
        f"Please confirm your email address by clicking the link below:\n\n"
        f"  {confirm_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you did not create an account, you can ignore this email.\n\n"
        f"— The Petso Team"
    )
    html_body = f"""
<html><body>
<p>Hi <strong>{user.name}</strong>,</p>
<p>Thanks for registering with <strong>Petso</strong>!</p>
<p>Please confirm your email address by clicking the button below:</p>
<p>
  <a href="{confirm_url}"
     style="background:#4CAF50;color:#fff;padding:12px 24px;
            text-decoration:none;border-radius:4px;display:inline-block;">
    Confirm Email
  </a>
</p>
<p>Or copy this link:<br><code>{confirm_url}</code></p>
<p>This link expires in <strong>24 hours</strong>.</p>
<p>If you did not create an account, you can ignore this email.</p>
<p>— The Petso Team</p>
</body></html>
"""
    from_email = settings.EMAIL_HOST_USER or "noreply@petso.app"

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.error("Failed to send confirmation email to %s: %s", user.email, exc)
        return False
