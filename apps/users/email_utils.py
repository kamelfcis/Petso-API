"""
Email confirmation helpers — direct Django send_mail (no Supabase redirect).

Flow:
  1. User registers → a UUID confirmation_token is saved on the User row.
  2. Django sends a plain HTML email via SMTP (configured in settings).
     The email contains a direct link:
       http://<PUBLIC_BASE_URL>/api/auth/confirm-email/<uuid>/
  3. User taps the link → browser opens Django directly (no redirect chain).
  4. Django looks up the UUID, marks is_email_verified=True, clears the token.
  5. Django renders the beautiful confirmation HTML page.
  6. After 3 s the page opens  petso://login  → Flutter app opens.
"""
import logging
import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import format_html

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _public_base_url() -> str:
    url = getattr(settings, "PETSO_PUBLIC_BASE_URL", "").strip().rstrip("/")
    return url or "http://95.216.63.81:8000"


def _from_email() -> str:
    return getattr(settings, "EMAIL_FROM", "noreply@petso.app")


# ── Token helpers ─────────────────────────────────────────────────────────────

def generate_confirmation_token(user) -> str:
    """
    Generate a fresh UUID token, store it on the user, and return it as string.
    Must be called before send_confirmation_email.
    """
    token = uuid.uuid4()
    user.confirmation_token = token
    user.save(update_fields=["confirmation_token"])
    return str(token)


# ── Email sending ─────────────────────────────────────────────────────────────

def send_confirmation_email(user) -> bool:
    """
    Send a confirmation email to *user* via Django's email backend (SMTP).

    The email contains a DIRECT link to our Django confirm-email endpoint.
    No Supabase redirect chain involved — the link opens Django immediately.

    Returns True on success, False on any error (logged, never raised).
    """
    try:
        token = generate_confirmation_token(user)
    except Exception as exc:
        logger.error("Failed to generate confirmation token for %s: %s", user.email, exc)
        return False

    confirm_url = f"{_public_base_url()}/api/auth/confirm-email/{token}/"

    subject = "Confirm your Petso account"

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/></head>
<body style="margin:0;padding:0;background:#f1f8e9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr><td align="center">
      <table width="520" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:20px;overflow:hidden;
                    box-shadow:0 4px 24px rgba(76,175,80,.12);">

        <!-- Header -->
        <tr>
          <td align="center"
              style="background:linear-gradient(135deg,#43a047,#66bb6a);padding:36px 40px 28px;">
            <h1 style="color:#fff;font-size:22px;font-weight:700;margin:18px 0 0;">
              Confirm Your Email
            </h1>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:36px 40px 28px;">
            <p style="font-size:16px;color:#37474f;line-height:1.7;margin:0 0 12px;">
              Hi {user.name}! 👋
            </p>
            <p style="font-size:16px;color:#37474f;line-height:1.7;margin:0 0 28px;">
              Thank you for signing up for <strong style="color:#2e7d32;">Petso</strong>.
              Tap the button below to confirm your email and activate your account.
            </p>

            <!-- CTA -->
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr><td align="center">
                <a href="{confirm_url}"
                   style="display:inline-block;background:linear-gradient(135deg,#43a047,#66bb6a);
                          color:#fff;font-size:16px;font-weight:700;text-decoration:none;
                          padding:16px 40px;border-radius:12px;
                          box-shadow:0 4px 16px rgba(76,175,80,.38);">
                  ✅ Confirm My Email
                </a>
              </td></tr>
            </table>

            <p style="font-size:14px;color:#90a4ae;margin:28px 0 0;line-height:1.6;">
              This link expires in <strong>24 hours</strong>.
              If you didn't create an account, ignore this email.
            </p>

            <!-- Fallback -->
            <div style="margin-top:20px;padding:14px 16px;background:#f9fbe7;
                        border-radius:10px;border:1px solid #dcedc8;">
              <p style="font-size:12px;color:#78909c;margin:0 0 6px;">
                Button not working? Copy and paste this link:
              </p>
              <p style="font-size:11px;color:#4caf50;word-break:break-all;margin:0;">
                {confirm_url}
              </p>
            </div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td align="center"
              style="background:#f9fbe7;padding:20px 40px;border-top:1px solid #f0f4c3;">
            <p style="font-size:12px;color:#aab4be;margin:0;">
              &copy; 2025 Petso &middot; All rights reserved<br/>
              <a href="mailto:support@petso.app" style="color:#81c784;text-decoration:none;">
                support@petso.app
              </a>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    plain_body = (
        f"Hi {user.name},\n\n"
        f"Please confirm your Petso account by visiting:\n{confirm_url}\n\n"
        f"This link expires in 24 hours.\n\nPetso Team"
    )

    try:
        send_mail(
            subject=subject,
            message=plain_body,
            from_email=_from_email(),
            recipient_list=[user.email],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info("Confirmation email sent to %s.", user.email)
        return True
    except Exception as exc:
        logger.error("Failed to send confirmation email to %s: %s", user.email, exc)
        return False
