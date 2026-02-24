from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == "booking":
        if not User.objects.filter(username="CLD").exists():
            User.objects.create_superuser(
                username="CLD",
                email="cld@example.com",
                password="CLD2025"
            )
