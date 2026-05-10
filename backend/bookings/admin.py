from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    fields = ('ticket_number', 'ticket_tier', 'attendee_name', 'status', 'checked_in', 'created_at')
    readonly_fields = ('ticket_number', 'created_at')
    show_change_link = True


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_number', 'user_link', 'event_link', 'status_badge', 'total_amount', 'ticket_count', 'created_at')
    list_filter = ('status', 'created_at', 'event__category')
    search_fields = ('booking_number', 'user__username', 'user__email', 'contact_email', 'contact_name', 'event__title')
    inlines = [TicketInline]
    readonly_fields = ('booking_number', 'created_at', 'updated_at')
    actions = ['confirm_bookings', 'cancel_bookings', 'mark_as_paid']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_number', 'event', 'user', 'status')
        }),
        ('Contact Details', {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        ('Financial', {
            'fields': ('total_amount', 'currency', 'subtotal', 'discount_amount', 'tax_amount')
        }),
        ('Additional', {
            'fields': ('special_requests', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        if obj.user:
            return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.user.id, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    
    def event_link(self, obj):
        return format_html('<a href="/admin/events/event/{}/change/">{}</a>', obj.event.id, obj.event.title)
    event_link.short_description = 'Event'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'confirmed': '#10b981',
            'cancelled': '#ef4444',
            'refunded': '#8b5cf6',
            'completed': '#6b7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    @admin.action(description='Confirm selected bookings')
    def confirm_bookings(self, request, queryset):
        queryset.update(status='confirmed')
    
    @admin.action(description='Cancel selected bookings')
    def cancel_bookings(self, request, queryset):
        queryset.update(status='cancelled')
    
    @admin.action(description='Mark as paid')
    def mark_as_paid(self, request, queryset):
        queryset.update(status='confirmed')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'booking_link', 'event_link', 'ticket_tier', 'attendee', 'status_badge', 'checked_in_status', 'created_at')
    list_filter = ('status', 'checked_in', 'created_at', 'ticket_tier__event__category')
    search_fields = ('ticket_number', 'attendee_name', 'attendee_email', 'booking__booking_number')
    readonly_fields = (
        'ticket_number',
        'security_code',
        'qr_code',
        'qr_code_data',
        'created_at',
        'updated_at',
    )
    date_hierarchy = 'created_at'
    actions = ['mark_as_valid', 'mark_as_used', 'check_in_tickets']
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'booking', 'ticket_tier', 'status')
        }),
        ('Attendee Details', {
            'fields': ('attendee_name', 'attendee_email', 'attendee_phone')
        }),
        ('Check-in', {
            'fields': ('checked_in', 'checked_in_at', 'checked_in_by')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_data', 'security_code'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def booking_link(self, obj):
        return format_html('<a href="/admin/bookings/booking/{}/change/">{}</a>', obj.booking.id, obj.booking.booking_number)
    booking_link.short_description = 'Booking'
    
    def event_link(self, obj):
        return format_html('<a href="/admin/events/event/{}/change/">{}</a>', obj.booking.event.id, obj.booking.event.title)
    event_link.short_description = 'Event'
    
    def attendee(self, obj):
        return f"{obj.attendee_name or '-'}"
    attendee.short_description = 'Attendee'
    
    def status_badge(self, obj):
        colors = {
            'valid': '#10b981',
            'used': '#6b7280',
            'cancelled': '#ef4444',
            'refunded': '#8b5cf6',
            'expired': '#f97316'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 11px; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def checked_in_status(self, obj):
        if obj.checked_in:
            return format_html('<span style="color: #10b981;">✓ Yes</span>')
        return format_html('<span style="color: #6b7280;">○ No</span>')
    checked_in_status.short_description = 'Checked In'
    
    @admin.action(description='Mark selected tickets as valid')
    def mark_as_valid(self, request, queryset):
        queryset.update(status='valid')
    
    @admin.action(description='Mark selected tickets as used')
    def mark_as_used(self, request, queryset):
        queryset.update(status='used')
    
    @admin.action(description='Check in selected tickets')
    def check_in_tickets(self, request, queryset):
        queryset.update(checked_in=True)
