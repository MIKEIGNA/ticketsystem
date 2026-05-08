from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, PaymentAttempt, Refund


class PaymentAttemptInline(admin.TabularInline):
    model = PaymentAttempt
    extra = 0
    fields = ('status', 'error_code', 'error_message', 'created_at')
    readonly_fields = ('status', 'error_code', 'error_message', 'request_payload', 'response_payload', 'created_at')
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_link', 'method_badge', 'amount_display', 'status_badge', 'mpesa_receipt', 'created_at')
    list_filter = ('status', 'method', 'created_at', 'currency')
    search_fields = ('booking__booking_number', 'mpesa_receipt_number', 'mpesa_checkout_request_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'completed_at')
    inlines = [PaymentAttemptInline]
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_failed', 'retry_payment']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'booking', 'method', 'status')
        }),
        ('Amount', {
            'fields': ('amount', 'currency', 'fees', 'net_amount')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_receipt_number', 'mpesa_checkout_request_id', 'mpesa_merchant_request_id', 'phone_number'),
            'classes': ('collapse',)
        }),
        ('Card Details', {
            'fields': ('card_last_four', 'card_brand'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    
    def booking_link(self, obj):
        return format_html('<a href="/admin/bookings/booking/{}/change/">{}</a>', obj.booking.id, obj.booking.booking_number)
    booking_link.short_description = 'Booking'
    
    def method_badge(self, obj):
        colors = {
            'mpesa': '#10b981',
            'card': '#3b82f6',
            'bank_transfer': '#8b5cf6',
            'paypal': '#f59e0b',
            'cash': '#6b7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; text-transform: uppercase;">{}</span>',
            colors.get(obj.method, '#6b7280'),
            obj.get_method_display()
        )
    method_badge.short_description = 'Method'
    
    def amount_display(self, obj):
        return f"{obj.currency} {obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'processing': '#3b82f6',
            'completed': '#10b981',
            'failed': '#ef4444',
            'cancelled': '#6b7280',
            'refunded': '#8b5cf6'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mpesa_receipt(self, obj):
        if obj.mpesa_receipt_number:
            return format_html('<span style="font-family: monospace; background: #f3f4f6; padding: 2px 6px; border-radius: 4px;">{}</span>', obj.mpesa_receipt_number)
        return '-'
    mpesa_receipt.short_description = 'M-Pesa Receipt'
    
    @admin.action(description='Mark selected payments as completed')
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    
    @admin.action(description='Mark selected payments as failed')
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
    
    @admin.action(description='Retry selected payments')
    def retry_payment(self, request, queryset):
        # This would typically trigger a background task to retry
        queryset.filter(status='failed').update(status='pending')


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_link', 'amount_display', 'status_badge', 'reason_short', 'requested_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__booking__booking_number', 'reason', 'admin_notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'processed_at')
    date_hierarchy = 'created_at'
    actions = ['approve_refunds', 'reject_refunds', 'process_refunds']
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('id', 'payment', 'amount', 'status')
        }),
        ('Reason', {
            'fields': ('reason', 'admin_notes')
        }),
        ('Processing', {
            'fields': ('requested_by', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">{}</a>', obj.payment.id, f"Payment #{obj.payment.id}")
    payment_link.short_description = 'Payment'
    
    def amount_display(self, obj):
        return f"{obj.payment.currency if obj.payment else 'KES'} {obj.amount:,.2f}"
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'requested': '#fbbf24',
            'approved': '#3b82f6',
            'rejected': '#ef4444',
            'completed': '#10b981',
            'failed': '#6b7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def reason_short(self, obj):
        if len(obj.reason) > 50:
            return obj.reason[:50] + '...'
        return obj.reason
    reason_short.short_description = 'Reason'
    
    @admin.action(description='Approve selected refunds')
    def approve_refunds(self, request, queryset):
        queryset.update(status='approved')
    
    @admin.action(description='Reject selected refunds')
    def reject_refunds(self, request, queryset):
        queryset.update(status='rejected')
    
    @admin.action(description='Mark selected refunds as completed')
    def process_refunds(self, request, queryset):
        queryset.update(status='completed')
