with open('pages/views.py', 'r') as f:
    content = f.read()

# Find and completely replace search_view
import re

# Simple working search_view
new_search = '''def search_view(request):
    q = (request.GET.get("q") or "").strip()
    qs = Profile.objects.filter(is_complete=True, is_approved=True).select_related("user").prefetch_related("images")
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q) |
            Q(headline__icontains=q) |
            Q(about__icontains=q) |
            Q(location__icontains=q)
        )
    paginator = Paginator(qs.order_by("-updated_at", "-created_at"), 12)
    page_obj = paginator.get_page(request.GET.get("page") or 1)
    for p in page_obj.object_list:
        p.card_image_url = _primary_image_url(p)
        p.card_age = _age_from_dob(getattr(p, "date_of_birth", None))
    return render(request, "pages/search.html", {"page_obj": page_obj, "total": paginator.count, "q": q})'''

# Replace the function
pattern = r'def search_view\(request\):.*?return render\(.*?\)'
new_content = re.sub(pattern, new_search, content, flags=re.DOTALL)

with open('pages/views.py', 'w') as f:
    f.write(new_content)

print("Replaced with minimal search_view")
