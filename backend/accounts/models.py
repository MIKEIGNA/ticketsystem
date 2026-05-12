import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


def normalize_phone(value: str) -> str:
    """
    Normalize a Kenyan phone number to 254XXXXXXXXX format.
    Accepts: 07XXXXXXXX, 01XXXXXXXX, 7XXXXXXXX, 1XXXXXXXX, 254XXXXXXXXX, +254XXXXXXXXX
    """
    if not value:
        return value
    phone = value.strip().lstrip('+')
    if phone.startswith('254') and len(phone) == 12 and phone.isdigit():
        return phone
    if phone.startswith('0') and len(phone) == 10 and phone.isdigit():
        return '254' + phone[1:]
    if len(phone) == 9 and phone.isdigit() and phone[0] in ('7', '1'):
        return '254' + phone
    return phone


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r'^(254[0-9]{9}|0[71][0-9]{8})$',
        message="Enter a valid Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, or 254XXXXXXXXX"
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        blank=True,
        null=True,
        unique=True,
        help_text="Kenyan phone number: 07XXXXXXXX, 01XXXXXXXX, or 254XXXXXXXXX"
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
