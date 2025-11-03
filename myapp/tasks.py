# from celery import shared_task
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import OTP
# from django.utils import timezone

# @shared_task(bind=True, retry_backoff=True, max_retries=3)
# def send_otp_email_task(self, otp_id):
#     """
#     Send OTP email asynchronously. Retries automatically on failure.
#     """
#     try:
#         otp = OTP.objects.select_related('user').get(id=otp_id)
#     except OTP.DoesNotExist:
#         return {"status": "missing", "otp_id": str(otp_id)}

#     if otp.is_used or otp.is_expired():
#         return {"status": "not_sent", "reason": "expired_or_used"}

#     user = otp.user
#     subject = "Your Verification Code"
#     context = {
#         "user": user,
#         "code": otp.code,
#         "expires_at": otp.expires_at,
#     }

#     text_body = f"Your verification code is {otp.code}. It expires at {otp.expires_at}."
#     html_body = render_to_string("emails/otp_email.html", context)

#     msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [user.email])
#     msg.attach_alternative(html_body, "text/html")

#     try:
#         msg.send(fail_silently=False)
#     except Exception as e:
#         raise self.retry(exc=e)

#     return {"status": "sent", "otp_id": str(otp_id)}


# @shared_task
# def cleanup_old_otps(days=7):
#     """Delete OTPs older than given days."""
#     cutoff = timezone.now() - timezone.timedelta(days=days)
#     OTP.objects.filter(created_at__lt=cutoff).delete()
