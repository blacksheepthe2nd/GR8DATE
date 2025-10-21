from django import template

register = template.Library()

@register.filter
def primary_image(images):
    return images.filter(is_primary=True).first()

@register.filter
def public_images(images):
    return images.filter(is_private=False, is_primary=False)

@register.filter
def private_images(images):
    return images.filter(is_private=True)
