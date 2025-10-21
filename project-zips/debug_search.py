# Read the file
with open('pages/views.py', 'r') as f:
    lines = f.readlines()

# Find the search_view function and add debug
for i, line in enumerate(lines):
    if 'def search_view(request):' in line:
        # Add debug after the function definition
        lines.insert(i + 1, '    print("=== SEARCH_VIEW CALLED ===\\n")\n')
        lines.insert(i + 2, '    print(f"Search query: {q}\\n")\n')
        break

# Write back
with open('pages/views.py', 'w') as f:
    f.writelines(lines)

print("Added debug to search_view")
