from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from data.models import Games, Subscriber, About
from django.template.loader import render_to_string


def send_new_game_email(game_instance):
    """
    Sends a new game email using a fresh Game instance from the DB.
    """
    # Fetch fresh object from DB to avoid cached/stale data
    game = Games.objects.get(pk=game_instance.pk)

    subject = f"⚡ NEW GAME DROP: {game.game_name}!"

    subscribers = Subscriber.objects.values_list("email", flat=True)
    if not subscribers:
        return

    html_content = render_to_string(
        "emails/new_game_email.html",
        {"game": game}  # always use fresh object
    )

    text_content = f"""
    New Game Alert: {game.game_name}
    Release Date: {game.release_date}
    Series: {game.series}
    Developer: {game.developer}
    Publisher: {game.publisher}
    """

    from_email = f"CyberCarnage <{settings.DEFAULT_FROM_EMAIL}>"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        list(subscribers),
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


@receiver(post_save, sender=About)
def notify_game_ready(sender, instance, created, **kwargs):
    if not created:
        return

    # Always fetch a fresh Game instance directly from DB
    game = Games.objects.get(pk=instance.game_id)
    send_new_game_email(game)
