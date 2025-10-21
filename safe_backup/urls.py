# pages/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Core Pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile Management
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    
    # Search & Discovery
    path('search/', views.search, name='search'),
    
    # Likes & Matching
    path('like/<int:user_id>/', views.like_user, name='like_user'),
    path('unfavorite/<int:user_id>/', views.unfavorite_user, name='unfavorite_user'),
    path('likes/received/', views.likes_received, name='likes_received'),
    path('likes/given/', views.likes_given, name='likes_given'),
    path('matches/', views.matches_list, name='matches_list'),
    
    # Messaging
    path('messages/', views.messages_combined, name='messages_list'),
    path('messages/<int:user_id>/', views.message_thread, name='message_thread'),
    path('messages/delete-conversation/<int:thread_id>/', views.delete_conversation, name='delete_conversation'),
    path('messages/unread-count/', views.messages_unread_count, name='messages_unread_count'),    
    
    # Private Photo Access
    path('request-private-access/<int:user_id>/', views.request_private_access, name='request_private_access'),
    path('approve-private-access/<int:request_id>/', views.approve_private_access, name='approve_private_access'),
    path('deny-private-access/<int:request_id>/', views.deny_private_access, name='deny_private_access'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    
    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Admin Approval System
    path('admin/approvals/', views.admin_profile_approvals, name='admin_profile_approvals'),
    path('admin/approve-profile/<int:profile_id>/', views.admin_approve_profile, name='admin_approve_profile'),
    path('admin/reject-profile/<int:profile_id>/', views.admin_reject_profile, name='admin_reject_profile'),
    
    # Blocking
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
]
