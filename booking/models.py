from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# ─── ROOM ────────────────────────────────────────────────────────────────────
class Room(models.Model):
    name           = models.CharField(max_length=100, unique=True)
    description    = models.CharField(max_length=255, blank=True)
    capacity       = models.PositiveIntegerField(default=0, help_text="Max attendees")
    tools          = models.CharField(max_length=255, blank=True, help_text="e.g. speaker, projector")
    tables         = models.PositiveIntegerField(default=0)
    chairs         = models.PositiveIntegerField(default=0)
    image          = models.ImageField(upload_to='room_images/', blank=True, null=True)
    projector      = models.CharField(max_length=3, choices=[("Yes","Yes"),("No","No")], default="No")
    speaker        = models.CharField(max_length=3, choices=[("Yes","Yes"),("No","No")], default="No")
    # 🆕 Pricing — used for billing per booking
    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Room rental cost per hour (PHP)"
    )

    def __str__(self):
        return self.name


# ─── PROFILE ─────────────────────────────────────────────────────────────────
class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    color = models.CharField(max_length=7, default='#6366F1')

    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


# ─── BOOKING ─────────────────────────────────────────────────────────────────
class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending",  "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    title      = models.CharField(max_length=200)
    attendees  = models.PositiveIntegerField(default=1)
    start      = models.DateTimeField()
    end        = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    color      = models.CharField(max_length=7, blank=True, null=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    # 🆕 Billing — auto-computed on every save
    hours_used = models.DecimalField(max_digits=6,  decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.start and self.end:
            delta = (self.end - self.start).total_seconds() / 3600
            self.hours_used = round(delta, 2)
            try:
                room = Room.objects.get(pk=self.room_id)
                self.total_cost = round(float(self.hours_used) * float(room.price_per_hour), 2)
            except Room.DoesNotExist:
                self.total_cost = 0
        super().save(*args, **kwargs)

    def display_color(self):
        return self.color or getattr(self.created_by.profile, 'color', '#6366F1')

    def __str__(self):
        return f"{self.title} ({self.room})"


# ─── TRIP ────────────────────────────────────────────────────────────────────
class Trip(models.Model):
    destination = models.CharField(max_length=200)
    date        = models.DateField()
    time        = models.TimeField(blank=True, null=True)
    notes       = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')

    def __str__(self):
        return f"{self.destination} on {self.date}"


# ─── HOLIDAY ─────────────────────────────────────────────────────────────────
class Holiday(models.Model):
    date        = models.DateField(unique=True)
    name        = models.CharField(max_length=200)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.date})"


# ─── PASSWORD CHANGE REQUEST ──────────────────────────────────────────────────
class PasswordChangeRequest(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    new_password = models.CharField(max_length=128)
    approved     = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    notified     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} — {'Approved' if self.approved else 'Pending'}"


# ─── 🆕 TODO LIST ─────────────────────────────────────────────────────────────
class Todo(models.Model):
    PRIORITY_CHOICES = [
        ("Low",    "Low"),
        ("Medium", "Medium"),
        ("High",   "High"),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    title      = models.CharField(max_length=200)
    note       = models.TextField(blank=True)
    priority   = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="Medium")
    due_date   = models.DateField(blank=True, null=True)
    is_done    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_done', '-created_at']

    def __str__(self):
        return f"[{self.user.username}] {self.title}"


# ─── 🆕 CHAT MESSAGE ──────────────────────────────────────────────────────────
class ChatMessage(models.Model):
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"


# ─── 🆕 FUTURE PROJECT ────────────────────────────────────────────────────────
class FutureProject(models.Model):
    STATUS_CHOICES = [
        ("Planned",     "Planned"),
        ("In Progress", "In Progress"),
        ("Done",        "Done"),
        ("Cancelled",   "Cancelled"),
    ]
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(blank=True, null=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Planned")
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at  = models.DateTimeField(auto_now_add=True)
    # TESDA / external training info
    provider    = models.CharField(max_length=200, blank=True, help_text="e.g. TESDA, External Trainer")
    budget      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['target_date']

    def __str__(self):
        return self.title
