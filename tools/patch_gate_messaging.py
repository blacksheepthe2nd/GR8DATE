import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
views = ROOT / "pages" / "views.py"
urls  = ROOT / "pages" / "urls.py"

def backup(p: pathlib.Path):
    bak = p.with_suffix(p.suffix + ".bak")
    bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return bak

def ensure_import(lines):
    txt = "".join(lines)
    changed = False
    if "from functools import wraps" not in txt:
        # insert near other imports, after django imports block
        for i, line in enumerate(lines):
            if line.strip().startswith("from django.views.generic"):
                lines.insert(i+1, "from functools import wraps\n")
                changed = True
                break
        else:
            lines.insert(0, "from functools import wraps\n")
            changed = True
    return changed

DECORATOR_BLOCK = """
# --- full access gate (preview lock) ---
def full_access_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        me_profile = _ensure_profile(request.user)
        if not _allow_full_access(me_profile):
            messages.info(request, "Finish your profile and get approved to unlock messaging.")
            return redirect("preview")
        return view_func(request, *args, **kwargs)
    return _wrapped
"""

def ensure_decorator_block(lines):
    txt = "".join(lines)
    if "def full_access_required(" in txt:
        return False
    # put after helper functions if possible; otherwise after imports
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("# ==========================================================================") and "Helpers" in lines[i+1] if i+1 < len(lines) else False:
            # insert just after helpers header
            insert_at = i + 2
            break
    else:
        # fallback: after imports block
        for i, line in enumerate(lines):
            if line.strip().startswith("from django.views.generic"):
                insert_at = i + 1
                break
    lines.insert(insert_at, DECORATOR_BLOCK + "\n")
    return True

def add_full_access_to_view(lines, func_name):
    """
    Ensure:
    @login_required
    @full_access_required
    def func_name(...):
    """
    txt = "".join(lines)
    pattern = re.compile(rf"@login_required\s*\ndef\s+{func_name}\s*\(", re.MULTILINE)
    if pattern.search(txt):
        # needs @full_access_required inserted between
        new_lines = []
        changed = False
        i = 0
        while i < len(lines):
            if lines[i].strip().startswith("@login_required"):
                # look ahead: is next non-empty line @full_access_required already?
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                # if next line starts with def func_name(, insert decorator
                if j < len(lines) and lines[j].strip().startswith(f"def {func_name}("):
                    new_lines.append(lines[i])
                    new_lines.append("@full_access_required\n")
                    changed = True
                    i += 1
                    continue
            new_lines.append(lines[i])
            i += 1
        if changed:
            lines[:] = new_lines
        return changed

    # Case 2: already has both decorators or different order
    # Ensure exists anywhere:
    if re.search(rf"def\s+{func_name}\s*\(", txt):
        # If it already has @full_access_required above, do nothing
        around = re.search(rf"(@[^\n]+\n)*def\s+{func_name}\s*\(", txt)
        if around and "@full_access_required" in around.group(0):
            return False
        # Otherwise, try to insert one line above def
        new_lines = []
        changed = False
        for i, line in enumerate(lines):
            if re.match(rf"\s*def\s+{func_name}\s*\(", line):
                new_lines.append("@full_access_required\n")
                new_lines.append(line)
                changed = True
            else:
                new_lines.append(line)
        lines[:] = new_lines
        return changed
    return False  # function not found

def patch_views():
    if not views.exists():
        print("ERROR: pages/views.py not found", file=sys.stderr)
        return 1
    content = views.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    backup(views)
    changed = False
    changed |= ensure_import(lines)
    changed |= ensure_decorator_block(lines)
    for fn in ("messages_inbox", "messages_thread_detail", "messages_send", "messages_unread_count"):
        c = add_full_access_to_view(lines, fn)
        changed |= bool(c)
    if changed:
        views.write_text("".join(lines), encoding="utf-8")
        print("Patched pages/views.py (backup created).")
    else:
        print("No changes needed in pages/views.py.")
    return 0

def patch_urls():
    if not urls.exists():
        print("WARNING: pages/urls.py not found; skipping alias patch.")
        return 0
    content = urls.read_text(encoding="utf-8")
    if "name=\"messages\"" in content:
        print("Alias 'messages' already present.")
        return 0
    # insert alias line right after messages_inbox line
    inbox_line = 'path("messages/", messages_inbox, name="messages_inbox"),'
    alias_line = '    path("messages/", messages_inbox, name="messages"),  # alias for legacy reverse\n'
    if inbox_line in content:
        backup(urls)
        content = content.replace(inbox_line + "\n", inbox_line + "\n" + alias_line)
        urls.write_text(content, encoding="utf-8")
        print("Added alias route 'messages' in pages/urls.py (backup created).")
    else:
        print("Could not find messages_inbox route; skipping alias injection.")
    return 0

if __name__ == "__main__":
    e1 = patch_views()
    e2 = patch_urls()
    sys.exit(e1 or e2)
