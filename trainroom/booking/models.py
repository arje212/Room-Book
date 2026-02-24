from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 🔹 Room model (single definition, with all fields)
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=0, help_text="Max attendees")
    tools = models.CharField(max_length=255, blank=True, help_text="List of tools (speaker, projector...)")
    tables = models.PositiveIntegerField(default=0)
    chairs = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    projector = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], default="No")
    speaker = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], default="No")

    def __str__(self):
        return self.name

# 🔹 Profile model for user color
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    color = models.CharField(max_length=7, default='#6366F1')  # default indigo

    def __str__(self):
        return f"{self.user.username} Profile"

# 🔹 Signal para auto-create Profile kapag may bagong User
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 🔹 Booking model
class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    title = models.CharField(max_length=200)
    attendees = models.PositiveIntegerField(default=1)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    color = models.CharField(max_length=7, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    def display_color(self):
        return self.color or getattr(self.created_by.profile, 'color', '#6366F1')

    def __str__(self):
        return f"{self.title} ({self.room})"

# 🔹 Trip model
class Trip(models.Model):
    destination = models.CharField(max_length=200)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')

    def __str__(self):
        return f"{self.destination} on {self.date}"

# 🔹 Holiday model
class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.date})"

# 🔹 PasswordChangeRequest model
class PasswordChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_password = models.CharField(max_length=128)
    approved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)  # ✅ dagdag

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.approved else 'Pending'}"
