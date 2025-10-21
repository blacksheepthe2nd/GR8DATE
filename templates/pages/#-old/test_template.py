from django.template import Template, Context
from pages.models import Profile

# Test if template rendering works
template_string = """
<p>Test: {{ total }}</p>
{% for p in page_obj %}{{ p.user.username }}{% endfor %}
"""

profiles = Profile.objects.all()[:2]
context = Context({
    'page_obj': profiles,
    'total': len(profiles),
    'q': 'test'
})

template = Template(template_string)
result = template.render(context)
print("Template result:", result)
