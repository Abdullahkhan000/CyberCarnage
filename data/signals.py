from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from data.models import Games, Subscriber, About
from django.template.loader import render_to_string

def send_new_game_email(instance):
    subject = f"⚡ NEW GAME DROP: {instance.game_name}!"

    subscribers = Subscriber.objects.values_list("email", flat=True)
    if not subscribers:
        return

    html_content = render_to_string(
        "emails/new_game_email.html",
        {"game": instance}
    )

    text_content = f"""
    New Game Alert: {instance.game_name}
    Release Date: {instance.release_date}
    Series: {instance.series}
    Developer: {instance.developer}
    Publisher: {instance.publisher}
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
    game = Games.objects.get(pk=instance.game.pk)
    send_new_game_email(game)