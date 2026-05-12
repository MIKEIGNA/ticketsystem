from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html, mark_safe
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('date_of_birth', 'city', 'country', 'id_number', 'emergency_contact_name', 'emergency_contact_phone')
    classes = ('wide',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'phone_display', 'organizer_badge', 'verified_badge', 'is_active', 'date_joined')
    list_filter = ('is_organizer', 'is_verified', 'is_staff', 'is_active', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    list_editable = ('is_active',)
    actions = ['verify_users', 'make_organizers', 'activate_users', 'deactivate_users']
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Profile', {
            'fields': ('profile_picture',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_organizer', 'is_verified', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )
    
    def phone_display(self, obj):
        if obj.phone_number:
            return format_html('<span style="font-family: monospace;">{}</span>', obj.phone_number)
        return '-'
    phone_display.short_description = 'Phone'
    
    def organizer_badge(self, obj):
        if obj.is_organizer:
            return mark_safe('<span style="background: #8b5cf6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px;">ORGANIZER</span>')
        return ''
    organizer_badge.short_description = 'Organizer'
    
    def verified_badge(self, obj):
        if obj.is_verified:
            return mark_safe('<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px;">✓ VERIFIED</span>')
        return mark_safe('<span style="background: #fbbf24; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px;">PENDING</span>')
    verified_badge.short_description = 'Verified'
    
    @admin.action(description='Mark selected users as verified')
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
    
    @admin.action(description='Make selected users organizers')
    def make_organizers(self, request, queryset):
        queryset.update(is_organizer=True)
    
    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'full_name', 'city', 'country', 'date_of_birth')
    list_filter = ('country', 'city')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'id_number')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'city', 'country', 'id_number')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        })
    )
    
    def user_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.user.id, obj.user.username)
    user_link.short_description = 'User'
    
    def full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or '-'
    full_name.short_description = 'Full Name'
