from django.contrib import admin, messages
from django.utils.html import format_html
from django.core.management import call_command
from .models import Category, Venue, Event, TicketTier


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_preview', 'slug', 'is_active', 'order', 'event_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background: {}; border-radius: 4px; border: 1px solid #ddd;"></div>',
            obj.color or '#ccc'
        )
    color_preview.short_description = 'Color'
    
    def event_count(self, obj):
        return obj.events.filter(status='published').count()
    event_count.short_description = 'Events'


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'capacity', 'is_active', 'event_count')
    list_filter = ('city', 'country', 'is_active')
    search_fields = ('name', 'address', 'city', 'country')
    list_editable = ('is_active',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('capacity', 'parking_info', 'accessibility_info')
        }),
        ('Contact', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    def event_count(self, obj):
        return obj.events.filter(status='published').count()
    event_count.short_description = 'Events'


class TicketTierInline(admin.TabularInline):
    model = TicketTier
    extra = 1
    fields = ('name', 'price', 'total_quantity', 'available_quantity', 'min_per_order', 'max_per_order', 'is_active')
    show_change_link = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'venue', 'start_datetime', 'status_badge', 'featured', 'view_count')
    list_filter = ('status', 'featured', 'category', 'venue__city', 'start_datetime')
    search_fields = ('title', 'description', 'subtitle')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'
    inlines = [TicketTierInline]
    list_editable = ('featured',)
    actions = ['make_published', 'make_draft', 'make_cancelled', 'duplicate_event', 'import_fkf_fixtures']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'slug', 'description', 'category')
        }),
        ('Media', {
            'fields': ('poster_image', 'banner_image')
        }),
        ('Date & Time', {
            'fields': ('start_datetime', 'end_datetime', 'doors_open')
        }),
        ('Venue & Location', {
            'fields': ('venue', 'is_public')
        }),
        ('Organizer', {
            'fields': ('organizer',)
        }),
        ('Settings', {
            'fields': ('status', 'featured', 'tags')
        }),
        ('Analytics', {
            'fields': ('view_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    
    def status_badge(self, obj):
        colors = {
            'draft': '#fbbf24',
            'published': '#10b981',
            'cancelled': '#ef4444',
            'completed': '#6b7280',
            'sold_out': '#f97316'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; text-transform: uppercase;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    @admin.action(description='Mark selected events as published')
    def make_published(self, request, queryset):
        queryset.update(status='published')
    
    @admin.action(description='Mark selected events as draft')
    def make_draft(self, request, queryset):
        queryset.update(status='draft')
    
    @admin.action(description='Cancel selected events')
    def make_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    
    @admin.action(description='Duplicate selected events')
    def duplicate_event(self, request, queryset):
        for event in queryset:
            event.pk = None
            event.slug = f"{event.slug}-copy"
            event.status = 'draft'
            event.view_count = 0
            event.save()

    @admin.action(description='Import FKF fixtures (creates sports events)')
    def import_fkf_fixtures(self, request, queryset):
        try:
            call_command('import_fkf_fixtures')
            self.message_user(
                request,
                'Successfully imported FKF fixtures!',
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f'Error importing FKF fixtures: {str(e)}',
                messages.ERROR
            )


@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_link', 'price', 'available', 'sales_status', 'is_active')
    list_filter = ('is_active', 'event__category', 'sales_start', 'sales_end')
    search_fields = ('name', 'event__title', 'description')
    readonly_fields = ('sold_count', 'sold_percentage', 'is_on_sale')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event', 'name', 'description', 'price', 'currency')
        }),
        ('Quantity', {
            'fields': ('total_quantity', 'available_quantity', 'min_per_order', 'max_per_order')
        }),
        ('Sales Window', {
            'fields': ('sales_start', 'sales_end')
        }),
        ('Seat Information', {
            'fields': ('includes_seat', 'seat_section')
        }),
        ('Benefits', {
            'fields': ('benefits',)
        }),
        ('Status', {
            'fields': ('is_active', 'order', 'is_on_sale', 'sold_count', 'sold_percentage')
        })
    )
    
    def event_link(self, obj):
        return format_html('<a href="/admin/events/event/{}/change/">{}</a>', obj.event.id, obj.event.title)
    event_link.short_description = 'Event'
    
    def available(self, obj):
        return f"{obj.available_quantity} / {obj.total_quantity}"
    available.short_description = 'Available'
    
    def sales_status(self, obj):
        if obj.is_on_sale:
            return format_html('<span style="color: #10b981; font-weight: bold;">On Sale</span>')
        return format_html('<span style="color: #6b7280;">Not Available</span>')
    sales_status.short_description = 'Sales'
