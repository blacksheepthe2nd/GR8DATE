from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
import json
from datetime import datetime, timedelta

from .models import Blog, Profile, ProfileImage, Thread, Message, Block, UserActivity

# ─────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────
def format_json(data):
    """Format JSON data for display"""
    return mark_safe(f'<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto;">{json.dumps(data, indent=2, ensure_ascii=False)}</pre>')

# ─────────────────────────────────────────────────────────────
# Blog Admin
# ─────────────────────────────────────────────────────────────
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "created_at", "updated_at")
    list_filter = ("status", "created_at", "published_at")
    search_fields = ("title", "summary", "content", "slug")
    ordering = ("-published_at", "-created_at")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "published_at"

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "status", "published_at")
        }),
        ("Content", {
            "fields": ("summary", "content")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    actions = ["publish_now", "mark_scheduled", "mark_draft"]

    @admin.action(description="Publish selected blogs now")
    def publish_now(self, request, queryset):
        updated = queryset.update(status=Blog.Status.PUBLISHED, published_at=timezone.now())
        self.message_user(request, f"Published {updated} blog(s).")

    @admin.action(description="Mark selected as scheduled")
    def mark_scheduled(self, request, queryset):
        updated = queryset.update(status=Blog.Status.SCHEDULED)
        self.message_user(request, f"Marked {updated} blog(s) as scheduled.")

    @admin.action(description="Mark selected as draft")
    def mark_draft(self, request, queryset):
        updated = queryset.update(status=Blog.Status.DRAFT)
        self.message_user(request, f"Marked {updated} blog(s) as draft.")


# ─────────────────────────────────────────────────────────────
# Profile Admin + Inline Images + Actions with WARNINGS
# ─────────────────────────────────────────────────────────────
class ProfileImageInline(admin.TabularInline):
    model = ProfileImage
    extra = 0
    fields = ("image", "image_preview", "is_primary", "is_private", "created_at")
    readonly_fields = ("created_at", "image_preview")

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />')
        return "-"


class AdminSendMessageForm(forms.Form):
    text = forms.CharField(
        label="Message text",
        widget=forms.Textarea(attrs={"rows": 4, "style": "width: 80%"}),
        help_text="This will be sent as a 1:1 message from you to each selected user.",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_username",
        "user_email",
        "approval_status_badge",
        "completion_status_badge", 
        "location",
        "user_activity_summary",
        "preview_profile_link_short",
    )
    list_filter = ("is_complete", "is_approved", "location", "created_at")
    search_fields = ("user__username", "user__email", "headline", "about", "location")
    ordering = ("-id",)
    inlines = [ProfileImageInline]
    readonly_fields = ("preview_profile_link", "created_at", "updated_at", "approval_warning", "activity_summary")
    list_select_related = ("user",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user__useractivity_set')

    fieldsets = (
        ("⚠️ Approval Status", {
            "fields": ("approval_warning", "is_complete", "is_approved"),
            "classes": ("alert", "warning"),
        }),
        ("User", {
            "fields": ("user",)
        }),
        ("Basics", {
            "fields": ("headline", "about", "location", "date_of_birth")
        }),
        ("Preferences", {
            "classes": ("collapse",),
            "fields": (
                "my_gender", "looking_for", "children", "my_interests",
                "must_have_tags", "preferred_age_min", "preferred_age_max",
                "preferred_distance", "preferred_intent",
            ),
        }),
        ("User Activity", {
            "classes": ("collapse",),
            "fields": ("activity_summary",)
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at")
        }),
        ("Review", {
            "fields": ("preview_profile_link",)
        }),
    )

    actions = (
        "action_mark_complete",
        "action_approve",
        "action_approve_and_complete", 
        "action_revoke_approval",
        "action_send_message_to_selected",
        "action_export_pending_approval",
    )

    # ---- WARNING DISPLAYS ----
    @admin.display(description="⚠️ Status Alert")
    def approval_warning(self, obj):
        if not obj.is_complete and not obj.is_approved:
            return mark_safe(
                '<div style="background: #fff3cd; border: 1px solid #ffeaa7; '
                'padding: 10px; border-radius: 4px; color: #856404;">'
                '🚨 <strong>ATTENTION NEEDED:</strong> Profile is incomplete AND unapproved'
                '</div>'
            )
        elif not obj.is_approved and obj.is_complete:
            return mark_safe(
                '<div style="background: #fff3cd; border: 1px solid #ffeaa7; '
                'padding: 10px; border-radius: 4px; color: #856404;">'
                '⚠️ <strong>PENDING APPROVAL:</strong> Profile complete but waiting approval'
                '</div>'
            )
        elif not obj.is_complete:
            return mark_safe(
                '<div style="background: #e7f3ff; border: 1px solid #b3d9ff; '
                'padding: 10px; border-radius: 4px; color: #004085;">'
                'ℹ️ <strong>INCOMPLETE:</strong> Profile needs completion'
                '</div>'
            )
        else:
            return mark_safe(
                '<div style="background: #d4edda; border: 1px solid #c3e6cb; '
                'padding: 10px; border-radius: 4px; color: #155724;">'
                '✅ <strong>APPROVED & COMPLETE</strong>'
                '</div>'
            )

    @admin.display(description="Approval")
    def approval_status_badge(self, obj):
        if obj.is_approved:
            return mark_safe(
                '<span style="background: #28a745; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 12px; font-weight: bold;">APPROVED</span>'
            )
        else:
            return mark_safe(
                '<span style="background: #ffc107; color: #856404; padding: 4px 8px; '
                'border-radius: 12px; font-size: 12px; font-weight: bold; animation: blink 2s infinite;">'
                '⚠️ PENDING</span>'
            )

    @admin.display(description="Completion") 
    def completion_status_badge(self, obj):
        if obj.is_complete:
            return mark_safe(
                '<span style="background: #17a2b8; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 12px; font-weight: bold;">COMPLETE</span>'
            )
        else:
            return mark_safe(
                '<span style="background: #dc3545; color: white; padding: 4px 8px; '
                'border-radius: 12px; font-size: 12px; font-weight: bold;">INCOMPLETE</span>'
            )

    @admin.display(description="Recent Activity")
    def user_activity_summary(self, obj):
        recent_activities = UserActivity.objects.filter(user=obj.user).order_by('-timestamp')[:3]
        if not recent_activities:
            return mark_safe('<span style="color: #6c757d;">No activity</span>')
        
        activities_html = []
        for activity in recent_activities:
            time_ago = timezone.now() - activity.timestamp
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600}h ago"
            else:
                time_str = f"{time_ago.seconds // 60}m ago"
                
            activities_html.append(
                f'<span style="font-size: 11px; background: #e9ecef; padding: 2px 6px; '
                f'border-radius: 8px; margin: 1px; display: inline-block;" title="{activity.timestamp}">'
                f'{activity.get_action_display()} • {time_str}</span>'
            )
        
        return mark_safe(' '.join(activities_html))

    @admin.display(description="Activity Summary")
    def activity_summary(self, obj):
        activities = UserActivity.objects.filter(user=obj.user).order_by('-timestamp')[:10]
        if not activities:
            return "No user activity recorded"
        
        summary = []
        for activity in activities:
            summary.append(
                f"• {activity.timestamp.strftime('%Y-%m-%d %H:%M')} - "
                f"{activity.get_action_display()} - "
                f"IP: {activity.ip_address or 'N/A'}"
            )
        
        return mark_safe(
            '<div style="max-height: 200px; overflow-y: auto; background: #f8f9fa; '
            'padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px;">'
            '<strong>Last 10 Activities:</strong><br>' + 
            '<br>'.join(summary) + 
            '</div>'
        )

    # ---- Display helpers
    @admin.display(description="Username", ordering="user__username")
    def user_username(self, obj):
        return getattr(obj.user, "username", "-")

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return getattr(obj.user, "email", "-")

    @admin.display(description="Preview")
    def preview_profile_link_short(self, obj):
        if obj.pk:
            url = f"/profile/{obj.pk}/"
            return mark_safe(f'<a href="{url}" target="_blank" rel="noopener">🔗 Open</a>')
        return "-"

    @admin.display(description="Full preview link")
    def preview_profile_link(self, obj):
        if obj.pk:
            url = f"/profile/{obj.pk}/"
            return mark_safe(f'<a href="{url}" target="_blank" rel="noopener">{url}</a>')
        return "No profile ID"

    # ---- Status actions
    @admin.action(description="✅ Mark selected as complete")
    def action_mark_complete(self, request, queryset):
        updated = queryset.update(is_complete=True)
        self.message_user(request, f"✅ Marked {updated} profile(s) as complete.", level='SUCCESS')

    @admin.action(description="✅ Approve selected profiles")
    def action_approve(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"✅ Approved {updated} profile(s).", level='SUCCESS')

    @admin.action(description="🚀 Approve + Mark complete")
    def action_approve_and_complete(self, request, queryset):
        updated = queryset.update(is_approved=True, is_complete=True)
        self.message_user(request, f"🚀 Approved & completed {updated} profile(s).", level='SUCCESS')

    @admin.action(description="⛔ Revoke approval")
    def action_revoke_approval(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"⛔ Revoked approval for {updated} profile(s).", level='WARNING')

    @admin.action(description="📊 Export pending approval list")
    def action_export_pending_approval(self, request, queryset):
        pending = queryset.filter(is_complete=True, is_approved=False)
        self.message_user(
            request, 
            f"📊 Found {pending.count()} profiles pending approval that are marked complete.", 
            level='INFO'
        )

    # ---- Send message action (with intermediate form)
    @admin.action(description="💬 Send message to selected user(s)…")
    def action_send_message_to_selected(self, request, queryset):
        action_name = "action_send_message_to_selected"
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        index = request.POST.get("index", "0")
        select_across = request.POST.get("select_across", "0")

        # Step 1: show the form
        if "apply" not in request.POST:
            form = AdminSendMessageForm()
            context = dict(
                self.admin_site.each_context(request),
                title="Send message to selected user(s)",
                action_name=action_name,
                action_checkbox_name=ACTION_CHECKBOX_NAME,
                selected=selected,
                index=index,
                select_across=select_across,
                queryset=queryset,
                opts=self.model._meta,
                form=form,
            )
            return TemplateResponse(request, "admin/pages/send_message_action.html", context)

        # Step 2: process the form and send messages
        form = AdminSendMessageForm(request.POST)
        if not form.is_valid():
            context = dict(
                self.admin_site.each_context(request),
                title="Send message to selected user(s)",
                action_name=action_name,
                action_checkbox_name=ACTION_CHECKBOX_NAME,
                selected=selected,
                index=index,
                select_across=select_across,
                queryset=queryset,
                opts=self.model._meta,
                form=form,
            )
            return TemplateResponse(request, "admin/pages/send_message_action.html", context)

        text = form.cleaned_data["text"].strip()
        if not text:
            self.message_user(request, "❌ Message text cannot be empty.", level="error")
            return None

        sent = 0
        admin_user = request.user
        for profile in queryset.select_related("user"):
            user = getattr(profile, "user", None)
            if not user or not user.is_active or user == admin_user:
                continue
            thread = Thread.get_or_create_for(admin_user, user)
            Message.objects.create(
                thread=thread, 
                sender=admin_user, 
                recipient=user, 
                text=text
            )
            # Log this admin activity
            UserActivity.objects.create(
                user=admin_user,
                action='admin_message_sent',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                target_object=profile,
                extra_data={
                    'recipient': user.username,
                    'message_preview': text[:100] + ('...' if len(text) > 100 else ''),
                    'admin_action': True
                }
            )
            sent += 1

        self.message_user(request, f"✅ Sent message to {sent} user(s).")
        return None


# ─────────────────────────────────────────────────────────────
# User Activity Admin
# ─────────────────────────────────────────────────────────────
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 
        'user_with_email', 
        'action_badge', 
        'target_object_link',
        'ip_address',
        'session_info'
    )
    list_filter = (
        'action', 
        'timestamp',
        'user__profile__location',
    )
    search_fields = (
        'user__username', 
        'user__email', 
        'ip_address',
        'extra_data'
    )
    readonly_fields = (
        'timestamp', 
        'user', 
        'action', 
        'ip_address', 
        'user_agent',
        'target_object_link',
        'extra_data_display'
    )
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Activity Details', {
            'fields': (
                'user', 
                'action_badge', 
                'timestamp', 
                'ip_address',
                'session_info'
            )
        }),
        ('Target Object', {
            'fields': ('target_object_link',),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('user_agent', 'extra_data_display'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 
            'target_content_type'
        )
    
    @admin.display(description='User', ordering='user__username')
    def user_with_email(self, obj):
        return f"{obj.user.username} ({obj.user.email})"
    
    @admin.display(description='Action')
    def action_badge(self, obj):
        colors = {
            'login': 'success',
            'logout': 'secondary', 
            'view_profile': 'info',
            'update_profile': 'warning',
            'send_message': 'primary',
            'admin_message_sent': 'dark',
        }
        color = colors.get(obj.action, 'light')
        return mark_safe(
            f'<span class="badge bg-{color}" style="font-size: 11px;">{obj.get_action_display()}</span>'
        )
    
    @admin.display(description='Target Object')
    def target_object_link(self, obj):
        if obj.target_object_id and obj.target_content_type:
            try:
                target = obj.target_content_type.get_object_for_this_type(pk=obj.target_object_id)
                app_label = obj.target_content_type.app_label
                model_name = obj.target_content_type.model
                url = reverse(f'admin:{app_label}_{model_name}_change', args=[target.id])
                return mark_safe(f'<a href="{url}">{str(target)}</a>')
            except:
                return f"Deleted {obj.target_content_type}"
        return "-"
    
    @admin.display(description='Extra Data')
    def extra_data_display(self, obj):
        if obj.extra_data:
            return format_json(obj.extra_data)
        return "-"
    
    @admin.display(description='Session Info')
    def session_info(self, obj):
        # Show time ago
        time_ago = timezone.now() - obj.timestamp
        if time_ago.days > 0:
            return f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            return f"{time_ago.seconds // 3600}h ago"
        else:
            return f"{time_ago.seconds // 60}m ago"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────────────────────
# Profile Images Admin
# ─────────────────────────────────────────────────────────────
@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "profile_id_display", 
        "user_username",
        "image_preview",
        "is_primary", 
        "is_private", 
        "created_at"
    )
    list_filter = ("is_primary", "is_private", "created_at")
    search_fields = ("profile__user__username", "profile__user__email")
    readonly_fields = ("created_at", "image_preview")
    list_select_related = ("profile__user",)

    @admin.display(description="Profile ID")
    def profile_id_display(self, obj):
        return getattr(obj.profile, "id", "-")

    @admin.display(description="Username")
    def user_username(self, obj):
        return getattr(obj.profile.user, "username", "-")

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />')
        return "-"


# ─────────────────────────────────────────────────────────────
# Threads & Messages Admin - FIXED VERSION
# ─────────────────────────────────────────────────────────────
@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "user_a", "user_b", "message_count", "created_at")
    search_fields = ("user_a__username", "user_b__username")
    ordering = ("-created_at",)
    list_select_related = ("user_a", "user_b")
    readonly_fields = ("created_at",)  # ← REMOVED updated_at

    @admin.display(description="Messages")
    def message_count(self, obj):
        return obj.messages.count()


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "recipient", "short_text", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "recipient__username", "text")
    ordering = ("-created_at",)
    list_select_related = ("thread", "sender", "recipient")
    readonly_fields = ("created_at",)

    def get_fields(self, request, obj=None):
        if obj is None:
            return ("sender", "recipient", "text")
        return ("thread", "sender", "recipient", "text", "is_read", "created_at")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("thread", "sender", "recipient", "created_at")
        return ()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        User = get_user_model()
        if db_field.name == "sender":
            kwargs["queryset"] = User.objects.filter(
                is_active=True
            ).filter(
                models.Q(is_staff=True) | models.Q(is_superuser=True)
            )
        elif db_field.name == "recipient":
            kwargs["queryset"] = User.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change and obj.sender_id and obj.recipient_id:
            obj.thread = Thread.get_or_create_for(obj.sender, obj.recipient)
            obj.is_read = False
        super().save_model(request, obj, form, change)

    @admin.display(description="Message")
    def short_text(self, obj):
        return (obj.text or "")[:80] + ("..." if len(obj.text or "") > 80 else "")


# ─────────────────────────────────────────────────────────────
# Block Admin
# ─────────────────────────────────────────────────────────────
@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("id", "blocker", "blocked", "created_at")
    search_fields = ("blocker__username", "blocked__username")
    ordering = ("-created_at",)
    list_select_related = ("blocker", "blocked")
    readonly_fields = ("created_at",)


# ─────────────────────────────────────────────────────────────
# Django LogEntry Admin (Built-in admin logs)
# ─────────────────────────────────────────────────────────────
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag_badge', 'change_message_short')
    list_filter = ('action_time', 'content_type', 'action_flag')
    search_fields = ('user__username', 'object_repr', 'change_message')
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Action')
    def action_flag_badge(self, obj):
        if obj.action_flag == 1:  # Addition
            return mark_safe('<span class="badge bg-success">ADD</span>')
        elif obj.action_flag == 2:  # Change
            return mark_safe('<span class="badge bg-warning">CHANGE</span>')
        elif obj.action_flag == 3:  # Deletion
            return mark_safe('<span class="badge bg-danger">DELETE</span>')
        return mark_safe(f'<span class="badge bg-secondary">{obj.action_flag}</span>')

    @admin.display(description='Changes')
    def change_message_short(self, obj):
        return (obj.change_message or "")[:100] + ("..." if len(obj.change_message or "") > 100 else "")

# ─────────────────────────────────────────────────────────────
# Hot Dates Admin
# ─────────────────────────────────────────────────────────────
from .models import HotDate, HotDateParticipant, HotDateView

@admin.register(HotDate)
class HotDateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "host_username",
        "activity",
        "vibe", 
        "date_time",
        "area",
        "audience_badge",
        "group_size",
        "status_badges",
        "created_at"
    )
    list_filter = (
        "activity",
        "vibe", 
        "audience",
        "group_size",
        "is_active",
        "is_cancelled",
        "created_at",
        "date_time"
    )
    search_fields = (
        "host__username",
        "host__email", 
        "area",
        "title"
    )
    readonly_fields = ("created_at", "updated_at", "participants_count")
    list_select_related = ("host",)
    date_hierarchy = "date_time"
    ordering = ("-date_time",)
    
    fieldsets = (
        ("Host & Basic Info", {
            "fields": ("host", "title", "activity", "vibe")
        }),
        ("Date & Location", {
            "fields": ("date_time", "area", "duration")
        }),
        ("Group Settings", {
            "fields": ("budget", "group_size", "audience")
        }),
        ("Status", {
            "fields": ("is_active", "is_cancelled", "participants_count")
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at")
        }),
    )
    
    actions = ["cancel_hotdates", "activate_hotdates", "delete_hotdates"]
    
    @admin.display(description="Host", ordering="host__username")
    def host_username(self, obj):
        return getattr(obj.host, "username", "-")
    
    @admin.display(description="Audience")
    def audience_badge(self, obj):
        colors = {
            "anyone": "success",
            "women_only": "danger", 
            "men_only": "primary"
        }
        color = colors.get(obj.audience, "secondary")
        return mark_safe(
            f'<span class="badge bg-{color}" style="font-size: 11px;">{obj.get_audience_display()}</span>'
        )
    
    @admin.display(description="Status")
    def status_badges(self, obj):
        badges = []
        if not obj.is_active:
            badges.append('<span class="badge bg-secondary" style="font-size: 10px;">INACTIVE</span>')
        elif obj.is_cancelled:
            badges.append('<span class="badge bg-danger" style="font-size: 10px;">CANCELLED</span>')
        else:
            badges.append('<span class="badge bg-success" style="font-size: 10px;">ACTIVE</span>')
        
        if obj.is_upcoming:
            badges.append('<span class="badge bg-info" style="font-size: 10px;">UPCOMING</span>')
        else:
            badges.append('<span class="badge bg-warning" style="font-size: 10px;">PAST</span>')
            
        return mark_safe(" ".join(badges))
    
    @admin.display(description="Participants")
    def participants_count(self, obj):
        count = obj.participants.count()
        return f"{count} participant(s)"
    
    @admin.action(description="⛔ Cancel selected Hot Dates")
    def cancel_hotdates(self, request, queryset):
        updated = queryset.update(is_cancelled=True)
        self.message_user(request, f"⛔ Cancelled {updated} Hot Date(s).", level='WARNING')
    
    @admin.action(description="✅ Activate selected Hot Dates")
    def activate_hotdates(self, request, queryset):
        updated = queryset.update(is_active=True, is_cancelled=False)
        self.message_user(request, f"✅ Activated {updated} Hot Date(s).", level='SUCCESS')
    
    @admin.action(description="🗑️ Delete selected Hot Dates")
    def delete_hotdates(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"🗑️ Deleted {count} Hot Date(s).", level='SUCCESS')


@admin.register(HotDateParticipant)
class HotDateParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_username",
        "hot_date_activity", 
        "hot_date_host",
        "hot_date_time",
        "joined_at"
    )
    list_filter = ("joined_at", "hot_date__activity", "hot_date__host__username")
    search_fields = (
        "user__username",
        "user__email",
        "hot_date__activity", 
        "hot_date__host__username"
    )
    readonly_fields = ("joined_at",)
    list_select_related = ("user", "hot_date__host")
    ordering = ("-joined_at",)
    
    @admin.display(description="User", ordering="user__username")
    def user_username(self, obj):
        return getattr(obj.user, "username", "-")
    
    @admin.display(description="Hot Date", ordering="hot_date__activity")
    def hot_date_activity(self, obj):
        return getattr(obj.hot_date, "activity", "-")
    
    @admin.display(description="Host", ordering="hot_date__host__username")
    def hot_date_host(self, obj):
        return getattr(obj.hot_date.host, "username", "-")
    
    @admin.display(description="Date & Time", ordering="hot_date__date_time")
    def hot_date_time(self, obj):
        date_time = getattr(obj.hot_date, "date_time", None)
        if date_time:
            return date_time.strftime("%Y-%m-%d %H:%M")
        return "-"


@admin.register(HotDateView)
class HotDateViewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_username",
        "hot_date_activity",
        "hot_date_host", 
        "viewed_at"
    )
    list_filter = ("viewed_at", "hot_date__activity")
    search_fields = (
        "user__username",
        "user__email",
        "hot_date__activity",
        "hot_date__host__username"
    )
    readonly_fields = ("viewed_at",)
    list_select_related = ("user", "hot_date__host")
    ordering = ("-viewed_at",)
    
    @admin.display(description="User", ordering="user__username")
    def user_username(self, obj):
        return getattr(obj.user, "username", "-")
    
    @admin.display(description="Hot Date", ordering="hot_date__activity")
    def hot_date_activity(self, obj):
        return getattr(obj.hot_date, "activity", "-")
    
    @admin.display(description="Host", ordering="hot_date__host__username")
    def hot_date_host(self, obj):
        return getattr(obj.hot_date.host, "username", "-")
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
