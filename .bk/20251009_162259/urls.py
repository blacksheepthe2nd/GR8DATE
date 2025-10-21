# pages/urls.py
# pages/urls.py
from django.urls import path
from .views import (
    BlogListView, BlogDetailView,
    messages_inbox, messages_thread_detail, messages_send, messages_unread_count,
)

urlpatterns = [
    # Blog
    path("blog/", BlogListView.as_view(), name="blog"),
    path("blog/<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),

    # Messages
    path("messages/", messages_inbox, name="messages_inbox"),
    path("messages/", messages_inbox, name="messages"),  # ⬅️ alias so {% url 'messages' %} still works
    path("messages/<int:thread_id>/", messages_thread_detail, name="messages_thread"),
    path("messages/send/", messages_send, name="messages_send"),
    path("messages/unread-count/", messages_unread_count, name="messages_unread_count"),

    # Optional: backward-compat aliases (safe to remove later)
    path("messages/send-stub/", messages_send, name="messages_send_stub"),
    path("messages/unread-count-stub/", messages_unread_count, name="messages_unread_count_stub"),
]

