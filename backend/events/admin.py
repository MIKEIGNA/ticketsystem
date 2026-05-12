from django.contrib import admin, messages
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html, mark_safe
from django.utils.safestring import mark_safe

from .models import Category, Event, KPLTeam, TicketTier, Venue


# ── KPL Team Admin ────────────────────────────────────────────────────────────

@admin.register(KPLTeam)
class KPLTeamAdmin(admin.ModelAdmin):
    list_display = (
        "logo_preview", "name", "short_name", "city",
        "home_stadium", "color_swatches", "founded", "is_active",
    )
    list_filter = ("is_active", "city")
    search_fields = ("name", "short_name", "city", "home_stadium")
    list_editable = ("is_active",)
    ordering = ("name",)
    actions = ["seed_kpl_data_action"]

    fieldsets = (
        ("Team Identity", {
            "fields": ("name", "short_name", "thesportsdb_id", "is_active"),
        }),
        ("Branding", {
            "fields": ("logo_url", "primary_color", "secondary_color"),
        }),
        ("Location", {
            "fields": ("home_stadium", "city", "founded"),
        }),
    )

    def logo_preview(self, obj):
        if obj.logo_url:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;object-fit:contain;'
                'border-radius:4px;background:#f3f4f6;padding:2px;" />',
                obj.logo_url,
            )
        return mark_safe('<span style="color:#9ca3af;">No logo</span>')
    logo_preview.short_description = "Logo"

    def color_swatches(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;background:{};'
            'border-radius:3px;border:1px solid #ddd;margin-right:4px;"></span>'
            '<span style="display:inline-block;width:18px;height:18px;background:{};'
            'border-radius:3px;border:1px solid #ddd;"></span>',
            obj.primary_color,
            obj.secondary_color,
        )
    color_swatches.short_description = "Colors"

    @admin.action(description="🌱 Seed / refresh all KPL teams & stadiums from built-in data")
    def seed_kpl_data_action(self, request, queryset):
        try:
            call_command("seed_kpl_data", update=True)
            self.message_user(
                request,
                "✓ KPL teams and stadiums seeded/refreshed successfully.",
                messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Error: {exc}", messages.ERROR)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "seed-kpl/",
                self.admin_site.admin_view(self._seed_kpl_view),
                name="events_kplteam_seed",
            ),
        ]
        return custom + urls

    def _seed_kpl_view(self, request):
        try:
            call_command("seed_kpl_data", update=True)
            self.message_user(
                request,
                "✓ KPL teams and stadiums seeded/refreshed successfully.",
                messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Error seeding data: {exc}", messages.ERROR)
        return HttpResponseRedirect(
            reverse("admin:events_kplteam_changelist")
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["seed_url"] = reverse("admin:events_kplteam_seed")
        return super().changelist_view(request, extra_context=extra_context)


# ── Category Admin ────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "color_preview", "slug", "is_active", "order", "event_count")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "order")

    def color_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border-radius:4px;'
            'border:1px solid #ddd;"></div>',
            obj.color or "#ccc",
        )
    color_preview.short_description = "Color"

    def event_count(self, obj):
        return obj.events.filter(status="published").count()
    event_count.short_description = "Events"


# ── Venue Admin ───────────────────────────────────────────────────────────────

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "capacity", "is_active", "event_count")
    list_filter = ("city", "country", "is_active")
    search_fields = ("name", "address", "city", "country")
    list_editable = ("is_active",)
    fieldsets = (
        ("Basic Information", {"fields": ("name", "description", "image")}),
        ("Location", {"fields": ("address", "city", "country", "latitude", "longitude")}),
        ("Details", {"fields": ("capacity", "parking_info", "accessibility_info")}),
        ("Contact", {"fields": ("contact_phone", "contact_email")}),
        ("Status", {"fields": ("is_active",)}),
    )

    def event_count(self, obj):
        return obj.events.filter(status="published").count()
    event_count.short_description = "Events"


# ── Ticket Tier Inline ────────────────────────────────────────────────────────

class TicketTierInline(admin.TabularInline):
    model = TicketTier
    extra = 1
    fields = (
        "name", "price", "total_quantity", "available_quantity",
        "min_per_order", "max_per_order", "is_active",
    )
    show_change_link = True


# ── Event Admin ───────────────────────────────────────────────────────────────

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "venue", "start_datetime",
        "status_badge", "featured", "view_count",
    )
    list_filter = ("status", "featured", "category", "venue__city", "start_datetime")
    search_fields = ("title", "description", "subtitle")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_datetime"
    inlines = [TicketTierInline]
    list_editable = ("featured",)
    actions = [
        "make_published", "make_draft", "make_cancelled", "duplicate_event",
        "sync_kpl_incremental", "sync_kpl_full", "import_fkf_fixtures_action",
        "cleanup_venues_action",
    ]

    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "subtitle", "slug", "description", "category"),
        }),
        ("⚽ Football Match Data", {
            "fields": ("home_team_selector", "away_team_selector", "match_data"),
            "classes": ("collapse",),
            "description": (
                "For football matches: select teams above to auto-fill logos & colors, "
                "or edit match_data JSON directly."
            ),
        }),
        ("Media", {"fields": ("poster_image", "banner_image")}),
        ("Date & Time", {"fields": ("start_datetime", "end_datetime", "doors_open")}),
        ("Venue & Location", {"fields": ("venue", "is_public")}),
        ("Organizer", {"fields": ("organizer",)}),
        ("Settings", {"fields": ("status", "featured", "tags", "age_restriction")}),
        ("Analytics", {"fields": ("view_count",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("view_count", "created_at", "updated_at", "home_team_selector", "away_team_selector")

    def home_team_selector(self, obj):
        """Read-only helper showing KPL team picker hint."""
        teams = KPLTeam.objects.filter(is_active=True).order_by("name")
        home = (obj.match_data or {}).get("home_team", "")
        options = "".join(
            f'<option value="{t.name}" {"selected" if t.name == home else ""}>{t.name}</option>'
            for t in teams
        )
        return format_html(
            '<select onchange="'
            'var d=JSON.parse(document.getElementById(\'id_match_data\').value||\'{{}}\');'
            'var t=this.options[this.selectedIndex];'
            'd.home_team=t.value;'
            'document.getElementById(\'id_match_data\').value=JSON.stringify(d,null,2);'
            '" style="width:300px;padding:4px;">'
            '<option value="">-- Select Home Team --</option>{}</select>',
            mark_safe(options),
        )
    home_team_selector.short_description = "Home Team (KPL)"

    def away_team_selector(self, obj):
        teams = KPLTeam.objects.filter(is_active=True).order_by("name")
        away = (obj.match_data or {}).get("away_team", "")
        options = "".join(
            f'<option value="{t.name}" {"selected" if t.name == away else ""}>{t.name}</option>'
            for t in teams
        )
        return format_html(
            '<select onchange="'
            'var d=JSON.parse(document.getElementById(\'id_match_data\').value||\'{{}}\');'
            'var t=this.options[this.selectedIndex];'
            'd.away_team=t.value;'
            'document.getElementById(\'id_match_data\').value=JSON.stringify(d,null,2);'
            '" style="width:300px;padding:4px;">'
            '<option value="">-- Select Away Team --</option>{}</select>',
            mark_safe(options),
        )
    away_team_selector.short_description = "Away Team (KPL)"

    def status_badge(self, obj):
        colors = {
            "draft": "#fbbf24",
            "published": "#10b981",
            "cancelled": "#ef4444",
            "completed": "#6b7280",
            "sold_out": "#f97316",
        }
        return format_html(
            '<span style="background:{};color:white;padding:4px 12px;border-radius:12px;'
            'font-size:12px;text-transform:uppercase;">{}</span>',
            colors.get(obj.status, "#6b7280"),
            obj.get_status_display(),
        )
    status_badge.short_description = "Status"

    # ── Bulk actions ──────────────────────────────────────────────────────────

    @admin.action(description="✅ Mark selected events as published")
    def make_published(self, request, queryset):
        queryset.update(status="published")

    @admin.action(description="📝 Mark selected events as draft")
    def make_draft(self, request, queryset):
        queryset.update(status="draft")

    @admin.action(description="❌ Cancel selected events")
    def make_cancelled(self, request, queryset):
        queryset.update(status="cancelled")

    @admin.action(description="📋 Duplicate selected events")
    def duplicate_event(self, request, queryset):
        for event in queryset:
            event.pk = None
            event.slug = f"{event.slug}-copy"
            event.status = "draft"
            event.view_count = 0
            event.save()
        self.message_user(request, f"Duplicated {queryset.count()} event(s) as drafts.", messages.SUCCESS)

    @admin.action(description="🔄 Sync KPL fixtures from TheSportsDB (incremental)")
    def sync_kpl_incremental(self, request, queryset):
        try:
            call_command("sync_thesportsdb_kpl", mode="incremental")
            self.message_user(
                request,
                "✓ KPL incremental sync complete. Check Events list for new/updated matches.",
                messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Sync failed: {exc}", messages.ERROR)

    @admin.action(description="🔄 Sync KPL full season from TheSportsDB")
    def sync_kpl_full(self, request, queryset):
        try:
            call_command("sync_thesportsdb_kpl", mode="full")
            self.message_user(
                request,
                "✓ KPL full season sync complete.",
                messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Sync failed: {exc}", messages.ERROR)

    @admin.action(description="⚽ Import hardcoded FKF fixtures (clears old, creates upcoming)")
    def import_fkf_fixtures_action(self, request, queryset):
        try:
            call_command("import_fkf_fixtures", clear_existing=True)
            self.message_user(request, "✓ FKF fixtures imported with upcoming dates.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Import failed: {exc}", messages.ERROR)

    @admin.action(description="🧹 Clean up bad venue names")
    def cleanup_venues_action(self, request, queryset):
        try:
            call_command("cleanup_bad_venues")
            self.message_user(request, "✓ Venue cleanup complete.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Cleanup failed: {exc}", messages.ERROR)

    # ── Custom top-level sync URLs ────────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "sync-kpl-incremental/",
                self.admin_site.admin_view(self._sync_incremental_view),
                name="events_event_sync_incremental",
            ),
            path(
                "sync-kpl-full/",
                self.admin_site.admin_view(self._sync_full_view),
                name="events_event_sync_full",
            ),
            path(
                "import-fkf/",
                self.admin_site.admin_view(self._import_fkf_view),
                name="events_event_import_fkf",
            ),
        ]
        return custom + urls

    def _sync_incremental_view(self, request):
        try:
            call_command("sync_thesportsdb_kpl", mode="incremental")
            self.message_user(
                request, "✓ KPL incremental sync complete.", messages.SUCCESS
            )
        except Exception as exc:
            self.message_user(request, f"Sync failed: {exc}", messages.ERROR)
        return HttpResponseRedirect(reverse("admin:events_event_changelist"))

    def _sync_full_view(self, request):
        try:
            call_command("sync_thesportsdb_kpl", mode="full")
            self.message_user(request, "✓ KPL full season sync complete.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Sync failed: {exc}", messages.ERROR)
        return HttpResponseRedirect(reverse("admin:events_event_changelist"))

    def _import_fkf_view(self, request):
        try:
            call_command("import_fkf_fixtures", clear_existing=True)
            self.message_user(request, "✓ FKF fixtures imported with upcoming dates.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Import failed: {exc}", messages.ERROR)
        return HttpResponseRedirect(reverse("admin:events_event_changelist"))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["sync_incremental_url"] = reverse("admin:events_event_sync_incremental")
        extra_context["sync_full_url"] = reverse("admin:events_event_sync_full")
        extra_context["import_fkf_url"] = reverse("admin:events_event_import_fkf")
        return super().changelist_view(request, extra_context=extra_context)


# ── Ticket Tier Admin ─────────────────────────────────────────────────────────

@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = ("name", "event_link", "price", "available", "sales_status", "is_active")
    list_filter = ("is_active", "event__category", "sales_start", "sales_end")
    search_fields = ("name", "event__title", "description")
    readonly_fields = ("sold_count", "sold_percentage", "is_on_sale")
    list_editable = ("is_active",)

    fieldsets = (
        ("Basic Information", {"fields": ("event", "name", "description", "price", "currency")}),
        ("Quantity", {"fields": ("total_quantity", "available_quantity", "min_per_order", "max_per_order")}),
        ("Sales Window", {"fields": ("sales_start", "sales_end")}),
        ("Seat Information", {"fields": ("includes_seat", "seat_section")}),
        ("Benefits", {"fields": ("benefits",)}),
        ("Status", {"fields": ("is_active", "order", "is_on_sale", "sold_count", "sold_percentage")}),
    )

    def event_link(self, obj):
        return format_html(
            '<a href="/admin/events/event/{}/change/">{}</a>',
            obj.event.id, obj.event.title,
        )
    event_link.short_description = "Event"

    def available(self, obj):
        return f"{obj.available_quantity} / {obj.total_quantity}"
    available.short_description = "Available"

    def sales_status(self, obj):
        if obj.is_on_sale:
            return format_html('<span style="color:#10b981;font-weight:bold;">On Sale</span>')
        return format_html('<span style="color:#6b7280;">Not Available</span>')
    sales_status.short_description = "Sales"
