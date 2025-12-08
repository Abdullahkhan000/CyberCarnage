from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from data.models import Games, Subscriber, About  # make sure About is imported


def send_new_game_email(instance):
    """Helper function to send email to subscribers"""
    subject = f"⚡ NEW GAME DROP: {instance.game_name}!"

    subscribers = Subscriber.objects.values_list("email", flat=True)
    if not subscribers:
        return

    html_content = f"""
    <div style="background:#050505;padding:32px;font-family:'Rajdhani',sans-serif;color:#d6d6d6;">
        <div style="max-width:720px;margin:auto;border-radius:18px;
                    background:#0d0d0d;border:1px solid #0ff;
                    box-shadow:0 0 22px rgba(0,255,255,0.18),0 0 45px rgba(180,0,255,0.12);
                    overflow:hidden;">
            <div style="padding:35px 30px;text-align:center;">
                <h1 style="font-family:'Orbitron',sans-serif;font-size:34px;
                           color:#00eaff;font-weight:600;margin:0;
                           text-shadow:0 0 10px #00ffff,0 0 22px #bc13fe;">
                    NEW GAME DROP
                </h1>
                <p style="color:#bfbfbf;font-size:14px;margin-top:10px;">
                    Fresh upload detected in the CyberCarnage vault.
                </p>
            </div>
            <div style="padding:30px 25px;background:#111;border-top:1px solid #0ff33f;">
                <h2 style="font-family:'Orbitron',sans-serif;font-size:27px;color:#bc13fe;
                           margin:0 0 10px 0;letter-spacing:1px;">
                    {instance.game_name}
                </h2>
                <div style="margin:14px 0;color:#9a9a9a;font-size:15px;line-height:1.6;">
                    <strong style="color:#00eaff;">Release Date:</strong> {instance.release_date}<br>
                    <strong style="color:#00eaff;">Series:</strong> {instance.series}<br>
                    <strong style="color:#00eaff;">Developer:</strong> {instance.developer}<br>
                    <strong style="color:#00eaff;">Publisher:</strong> {instance.publisher}
                </div>
                <div style="margin:25px 0;text-align:center;">
                    <a href="https://cyber-carnage.vercel.app/{instance.slug}/"
                       style="padding:14px 32px;font-weight:700;border-radius:10px;
                              font-family:'Orbitron',sans-serif;font-size:16px;letter-spacing:1px;
                              background:#00eaff;color:#000;text-decoration:none;
                              box-shadow:0 0 12px rgba(0,255,255,0.7),
                                         0 0 28px rgba(188,19,254,0.35);">
                        VIEW GAME
                    </a>
                </div>
            </div>
            <div style="padding:28px 20px;text-align:center;background:#0b0b0b;
                        border-top:1px solid #1a1a1a;">
                <p style="font-size:12px;color:#555;line-height:1.5;">
                    CyberCarnage • Gaming Updates<br>
                    You’re receiving this because you subscribed to notifications.
                </p>
            </div>
        </div>
    </div>
    """

    text_content = f"""
New Game Alert: {instance.game_name}

Release Date: {instance.release_date}
Series: {instance.series}
Developer: {instance.developer}
Publisher: {instance.publisher}

Visit CyberCarnage to check out the full details and explore more!
"""

    from_email = f"CyberCarnage <{settings.DEFAULT_FROM_EMAIL}>"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        list(subscribers)
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


# Trigger the email only when About is created (ensures game is fully populated)
@receiver(post_save, sender=About)
def notify_game_ready(sender, instance, created, **kwargs):
    if not created:
        return
    game = instance.game
    send_new_game_email(game)
