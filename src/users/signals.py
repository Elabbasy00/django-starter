from django.dispatch import receiver


from django.core.mail import EmailMultiAlternatives
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings
from django.template.loader import render_to_string

from config.env import env
import re


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    frontend_url = env.str("DJANGO_BASE_FRONTEND_URL", default="http://localhost:3000")

    context = {
        "current_user": reset_password_token.user,
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        "ip": reset_password_token.ip_address,
        "agent": re.findall(r"\(.*?\)", reset_password_token.user_agent)[0],
        "reset_password_url": "{}/auth/reset-password?token={}".format(
            frontend_url,
            reset_password_token.key,
        ),
    }

    # render email text
    email_html_message = render_to_string("email/password_reset_email.html", context)
    email_plaintext_message = render_to_string("email/password_reset_email.txt", context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Your Website Title"),
        # message:
        email_plaintext_message,
        # from:
        settings.DEFAULT_FROM_EMAIL,
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
