# pages/templatetags/profile_tags.py
from django import template
from ..models import Like, Block

register = template.Library()

@register.filter
def has_liked(user, target_user):
    """Check if user has liked target user"""
    if not user.is_authenticated:
        return False
    return Like.objects.filter(liker=user, liked_user=target_user).exists()

@register.filter
def has_blocked(user, target_user):
    """Check if user has blocked target user"""
    if not user.is_authenticated:
        return False
    return Block.objects.filter(blocker=user, blocked=target_user).exists()

@register.filter
def primary_image(images):
    return images.filter(is_primary=True).first()

@register.filter
def public_images(images):
    return images.filter(is_private=False, is_primary=False)

@register.filter
def private_images(images):
    return images.filter(is_private=True)
