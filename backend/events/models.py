import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    color = models.CharField(max_length=7, default="#000000", help_text="Hex color code")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Venue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='venues/', blank=True, null=True)
    parking_info = models.TextField(blank=True)
    accessibility_info = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=13, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.city}"


class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('sold_out', 'Sold Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='events')
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='events')
    organizer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='organized_events')
    
    # Event timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)
    doors_open = models.TimeField(blank=True, null=True, help_text="Time when doors open")
    
    # Media
    poster_image = models.ImageField(upload_to='events/posters/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='events/banners/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of image URLs")
    video_url = models.URLField(blank=True)
    
    # Event details
    age_restriction = models.CharField(max_length=50, blank=True, help_text="e.g., 18+, All Ages")
    dress_code = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False, help_text="Featured on homepage")
    tags = models.JSONField(default=list, blank=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['status', 'start_datetime']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_datetime.strftime('%Y-%m-%d')})"

    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

    @property
    def is_ongoing(self):
        if self.end_datetime:
            return self.start_datetime <= timezone.now() <= self.end_datetime
        return self.start_datetime <= timezone.now() < self.start_datetime + timezone.timedelta(hours=4)

    @property
    def days_until_event(self):
        if self.start_datetime > timezone.now():
            return (self.start_datetime - timezone.now()).days
        return 0


class TicketTier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_tiers')
    name = models.CharField(max_length=100, help_text="e.g., VIP, Regular, Early Bird")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='KES')
    
    # Quantity management
    total_quantity = models.PositiveIntegerField(help_text="Total tickets available for this tier")
    available_quantity = models.PositiveIntegerField(help_text="Currently available tickets")
    
    # Limits
    min_per_order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    max_per_order = models.PositiveIntegerField(default=10)
    
    # Sales window
    sales_start = models.DateTimeField(blank=True, null=True)
    sales_end = models.DateTimeField(blank=True, null=True)
    
    # Tier settings
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # Benefits
    includes_seat = models.BooleanField(default=False)
    seat_section = models.CharField(max_length=100, blank=True)
    benefits = models.JSONField(default=list, blank=True, help_text="List of included benefits")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'price']
        unique_together = ['event', 'name']

    def __str__(self):
        return f"{self.event.title} - {self.name} (KES {self.price})"

    @property
    def is_on_sale(self):
        now = timezone.now()
        if self.sales_start and now < self.sales_start:
            return False
        if self.sales_end and now > self.sales_end:
            return False
        return self.is_active and self.available_quantity > 0

    @property
    def sold_count(self):
        return self.total_quantity - self.available_quantity

    @property
    def sold_percentage(self):
        if self.total_quantity > 0:
            return (self.sold_count / self.total_quantity) * 100
        return 0

