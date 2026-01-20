from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from data.models import Games, Subscriber, About
import requests


# def send_new_game_email(about_instance):
#     game = about_instance.game
#     about = about_instance
#
#     subject = f"⚡ NEW GAME DROP: {game.game_name}!"
#
#     subscribers = Subscriber.objects.values_list("email", flat=True)
#     if not subscribers:
#         return
#
#     html_content = render_to_string(
#         "emails/new_game_email.html",
#         {"game": game, "about": about}
#     )
#
#     text_content = f"""
#     New Game Alert: {game.game_name}
#     Release Date: {game.release_date}
#     Series: {game.series}
#     Developer: {game.developer}
#     Publisher: {game.publisher}
#     """
#
#     from_email = f"CyberCarnage <{settings.DEFAULT_FROM_EMAIL}>"
#
#     email = EmailMultiAlternatives(
#         subject,
#         text_content,
#         from_email,
#         list(subscribers),
#     )
#     email.attach_alternative(html_content, "text/html")
#     email.send(fail_silently=False)

def send_new_game_email(about_instance):
    game = about_instance.game
    about = about_instance

    subject = f"⚡ NEW GAME DROP: {game.game_name}!"

    subscribers = Subscriber.objects.all()
    if not subscribers.exists():
        return

    html_content = render_to_string(
        "emails/new_game_email.html",
        {"game": game, "about": about}
    )

    for sub in subscribers:
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"CyberCarnage <{settings.DEFAULT_FROM_EMAIL}>",
                "to": [sub.email],
                "subject": subject,
                "html": html_content,
            },
            timeout=10
        )


@receiver(post_save, sender=About)
def notify_game_ready(sender, instance, created, **kwargs):
    if created:
        send_new_game_email(instance)
