from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from data.models import Games, Subscriber, About
import requests
import threading
import time

def send_email_to_subscriber(sub, subject, html_content, text_content):
    try:
        response = requests.post(
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
                "text": text_content,
                # Optional: "reply_to": "support@cybercarnage.online"
            },
            timeout=10
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send email to {sub.email}: {e}")


def send_new_game_email(about_instance):
    game = about_instance.game
    about = about_instance

    subject = f"⚡ NEW GAME DROP: {game.game_name}!"

    subscribers = Subscriber.objects.all()
    if not subscribers.exists():
        return

    html_content = render_to_string(
        "emails/new_game_email.html",
        {
            "game": game,
            "about": about,
            "unsubscribe_url": "{{unsubscribe_link}}"
        }
    )

    text_content = f"""
New Game Alert: {game.game_name}
Release Date: {game.release_date}
Series: {game.series}
Developer: {game.developer}
Publisher: {game.publisher}
Unsubscribe: {{unsubscribe_link}}
"""

    for sub in subscribers:
        response = requests.post(
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

        time.sleep(0.6)


@receiver(post_save, sender=About)
def notify_game_ready(sender, instance, created, **kwargs):
    if created:
        send_new_game_email(instance)
