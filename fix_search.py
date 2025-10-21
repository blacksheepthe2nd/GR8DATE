# Fix for search_view - only apply age filters when ages are provided
sed -i '' '330,335s/if dob_min:/if dob_min is not None:/' pages/views.py
sed -i '' '331,336s/if dob_max:/if dob_max is not None:/' pages/views.py
