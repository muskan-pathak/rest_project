from datetime import timedelta
import secrets

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

def generate_and_send_otp(user, subject, message_prefix):
    otp = f"{secrets.randbelow(900000) + 100000}"
    now = timezone.now()

    user.otp_hash = make_password(otp)
    user.otp_created_at = now
    user.otp_expires_at = now + timedelta(minutes=5)
    user.otp_is_used = False

    user.save(update_fields=[
        "otp_hash",
        "otp_created_at",
        "otp_expires_at",
        "otp_is_used",
    ])

    send_mail(
        subject=subject,
        message=f"{message_prefix}{otp}. It expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def validate_user_otp(user, otp):
    if (
        not user.otp_hash
        or not user.otp_expires_at
        or user.otp_is_used
        or user.otp_expires_at <= timezone.now()
    ):
        return False

    return check_password(otp, user.otp_hash)






def send_limited_otp(user, subject, message):
    now = timezone.now()

    # Check whether the user is already blocked
    if user.otp_blocked_until and now < user.otp_blocked_until:
        raise ValidationError(
            "You have exceeded the maximum number of OTP requests. "
            "Please try again after 12 hours."
        )

    # Start a new 12-hour window when needed
    if (
        user.otp_request_window_start is None
        or now >= user.otp_request_window_start + timedelta(hours=12)
    ):
        user.otp_request_count = 0
        user.otp_request_window_start = now
        user.otp_blocked_until = None

    # Block requests after 3 successful sends
    if user.otp_request_count >= 3:
        user.otp_blocked_until = now + timedelta(hours=12)
        user.save(update_fields=[
            "otp_request_count",
            "otp_request_window_start",
            "otp_blocked_until",
        ])
        raise ValidationError(
            "You have exceeded the maximum number of OTP requests. "
            "Please try again after 12 hours."
        )

    # Send OTP and count the successful send
    generate_and_send_otp(user, subject, message)

    user.otp_request_count += 1
    user.save(update_fields=[
        "otp_request_count",
        "otp_request_window_start",
        "otp_blocked_until",
    ])


def generate_unique_username(email):
    """Build a unique username from the part of the email before '@'."""
    from .models import User

    base = email.split("@")[0][:140]
    username = base
    counter = 1

    while User.objects.filter(username__iexact=username).exists():
        username = f"{base}{counter}"
        counter += 1

    return username

