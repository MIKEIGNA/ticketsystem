import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r'^254[0-9]{9}$',
        message="Phone number must be entered in the format: '254XXXXXXXXX'. Up to 12 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        blank=True,
        null=True,
        unique=True,
        help_text="M-Pesa phone number in format 254XXXXXXXXX"
    )
    is_organizer = models.BooleanField(default=False, help_text="Can create and manage events")
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.phone_number or 'No phone'})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Kenya')
    id_number = models.CharField(max_length=20, blank=True, help_text="National ID or Passport number")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=13, blank=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"

