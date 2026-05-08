import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_number = models.CharField(max_length=20, unique=True, db_index=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='bookings')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Totals
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    ticket_count = models.PositiveIntegerField(default=0)
    
    # Contact info (at time of booking)
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=13)
    
    # Notes
    special_requests = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="Booking expires if not paid")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'status']),
            models.Index(fields=['booking_number']),
        ]

    def __str__(self):
        return f"Booking #{self.booking_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        super().save(*args, **kwargs)

    def generate_booking_number(self):
        import random
        import string
        prefix = "TKT"
        timestamp = timezone.now().strftime('%y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{timestamp}{random_str}"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('used', 'Used'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=30, unique=True, db_index=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')
    ticket_tier = models.ForeignKey('events.TicketTier', on_delete=models.PROTECT, related_name='tickets')
    
    # Ticket details
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='valid')
    
    # Attendee info
    attendee_name = models.CharField(max_length=200, blank=True)
    attendee_email = models.EmailField(blank=True)
    attendee_phone = models.CharField(max_length=13, blank=True)
    
    # Seat assignment
    seat_number = models.CharField(max_length=20, blank=True)
    
    # QR Code
    qr_code = models.ImageField(upload_to='tickets/qr_codes/', blank=True, null=True)
    qr_code_data = models.TextField(blank=True, help_text="Data encoded in QR code")
    
    # Check-in
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='check_ins')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.ticket_tier.name}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        if not self.qr_code_data:
            self.qr_code_data = f"TICKET:{self.ticket_number}:{self.booking.event.id}"
        super().save(*args, **kwargs)
        
        # Generate QR code after save
        if not self.qr_code:
            self.generate_qr_code()

    def generate_ticket_number(self):
        import random
        import string
        prefix = self.booking.event.title[:3].upper()
        timestamp = timezone.now().strftime('%y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{timestamp}{random_str}"

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        filename = f'qr_{self.ticket_number}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        self.save(update_fields=['qr_code'])

    def check_in(self, checked_by=None):
        if not self.checked_in and self.status == 'valid':
            self.checked_in = True
            self.checked_in_at = timezone.now()
            self.checked_in_by = checked_by
            self.save(update_fields=['checked_in', 'checked_in_at', 'checked_in_by'])
            return True
        return False

