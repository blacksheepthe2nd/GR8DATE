# pages/admin.py
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Profile, Message, Thread, Like, Block, PrivateAccessRequest,
    HotDate, HotDateView, HotDateNotification, Blog, UserActivity, ProfileImage
)

# Inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend User Admin
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

# Model Admins
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'my_gender', 'looking_for', 'created_at')
    search_fields = ('user__username', 'headline', 'location', 'about')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_profiles', 'reject_profiles']

    def approve_profiles(self, request, queryset):
        queryset.update(is_approved=True)
    approve_profiles.short_description = "Approve selected profiles"

    def reject_profiles(self, request, queryset):
        queryset.update(is_approved=False)
    reject_profiles.short_description = "Reject selected profiles"

@admin.register(ProfileImage)
class ProfileImageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'image', 'is_private', 'is_primary', 'created_at')
    list_filter = ('is_private', 'is_primary')
    search_fields = ('profile__user__username',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('thread', 'sender', 'recipient', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('text', 'sender__username', 'recipient__username')
    readonly_fields = ('created_at',)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('user_a', 'user_b', 'created_at', 'updated_at')
    search_fields = ('user_a__username', 'user_b__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('liker', 'liked_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('liker__username', 'liked_user__username')
    readonly_fields = ('created_at',)

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked__username')
    readonly_fields = ('created_at',)

@admin.register(PrivateAccessRequest)
class PrivateAccessRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'target_user', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('requester__username', 'target_user__username')
    readonly_fields = ('created_at', 'reviewed_at')
    actions = ['approve_requests', 'deny_requests']

    def approve_requests(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
    approve_requests.short_description = "Approve selected requests"

    def deny_requests(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='denied', reviewed_by=request.user, reviewed_at=timezone.now())
    deny_requests.short_description = "Deny selected requests"

@admin.register(HotDate)
class HotDateAdmin(admin.ModelAdmin):
    list_display = ('host', 'activity', 'date_time', 'area', 'is_active', 'is_cancelled', 'created_at')
    list_filter = ('is_active', 'is_cancelled', 'date_time', 'created_at')
    search_fields = ('host__username', 'activity', 'area', 'vibe')
    readonly_fields = ('created_at', 'updated_at')  # FIXED: removed cancelled_at (doesn't exist)
    actions = ['activate_hotdates', 'deactivate_hotdates', 'cancel_hotdates']

    def activate_hotdates(self, request, queryset):
        queryset.update(is_active=True)
    activate_hotdates.short_description = "Activate selected Hot Dates"

    def deactivate_hotdates(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_hotdates.short_description = "Deactivate selected Hot Dates"

    def cancel_hotdates(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_cancelled=True)
    cancel_hotdates.short_description = "Cancel selected Hot Dates"

@admin.register(HotDateView)
class HotDateViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'hot_date', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'hot_date__activity')
    readonly_fields = ('viewed_at',)

@admin.register(HotDateNotification)
class HotDateNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'hot_date', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'hot_date__activity', 'message')
    readonly_fields = ('created_at', 'read_at')
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_read=True, read_at=timezone.now())
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False, read_at=None)
    mark_as_unread.short_description = "Mark selected notifications as unread"

# FIXED BlogAdmin - Blog model doesn't have 'user' field, it's a standalone model
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_at', 'created_at')  # REMOVED: 'user'/'author' - Blog is standalone
    list_filter = ('status', 'published_at', 'created_at')
    search_fields = ('title', 'content')  # REMOVED: 'user__username'/'author__username'
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=Blog.Status.PUBLISHED, published_at=timezone.now())
    publish_posts.short_description = "Publish selected blog posts"

    def unpublish_posts(self, request, queryset):
        queryset.update(status=Blog.Status.DRAFT, published_at=None)
    unpublish_posts.short_description = "Unpublish selected blog posts"

# FIXED UserActivityAdmin - uses 'action' field, not 'activity_type'
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')  # FIXED: 'activity_type' → 'action', 'created_at' → 'timestamp'
    list_filter = ('action', 'timestamp')  # FIXED: 'activity_type' → 'action', 'created_at' → 'timestamp'
    search_fields = ('user__username', 'action')  # FIXED: 'activity_type' → 'action'
    readonly_fields = ('timestamp',)  # FIXED: 'created_at' → 'timestamp'

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
