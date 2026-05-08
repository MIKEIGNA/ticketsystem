import uuid
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment')
    
    # Payment details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='mpesa')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # M-Pesa specific fields
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, db_index=True)
    mpesa_transaction_date = models.DateTimeField(blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=13, blank=True)
    mpesa_result_code = models.CharField(max_length=10, blank=True)
    mpesa_result_desc = models.TextField(blank=True)
    
    # Other payment methods
    transaction_reference = models.CharField(max_length=100, blank=True, help_text="Reference for non-M-Pesa payments")
    
    # Metadata
    payment_metadata = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['mpesa_receipt_number']),
            models.Index(fields=['mpesa_checkout_request_id']),
        ]

    def __str__(self):
        return f"Payment {self.id} - KES {self.amount} ({self.status})"

    def mark_completed(self, receipt_number=None):
        self.status = 'completed'
        if receipt_number:
            self.mpesa_receipt_number = receipt_number
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'mpesa_receipt_number', 'completed_at'])

    def mark_failed(self, reason=None, result_code=None, result_desc=None):
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        if result_code:
            self.mpesa_result_code = result_code
        if result_desc:
            self.mpesa_result_desc = result_desc
        self.save(update_fields=['status', 'failure_reason', 'mpesa_result_code', 'mpesa_result_desc'])


class PaymentAttempt(models.Model):
    """Track all payment attempts for audit purposes"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('stk_pushed', 'STK Push Sent'),
        ('user_cancelled', 'User Cancelled'),
        ('timeout', 'Timeout'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Request details
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    
    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Attempt {self.id} - {self.status}"


class Refund(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    # Requested by
    requested_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='requested_refunds')
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_refunds')
    
    # Processing details
    mpesa_reversal_receipt = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund {self.id} - KES {self.amount} ({self.status})"

