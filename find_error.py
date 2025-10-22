import pandas as pd

df = pd.read_csv("gr8date_complete_profiles.csv")

print("Checking for potential issues in the CSV...")
print(f"Total rows: {len(df)}")

# Check for missing data
for column in df.columns:
    missing = df[column].isna().sum()
    if missing > 0:
        print(f"Column '{column}': {missing} missing values")

# Check for duplicate usernames
duplicates = df[df.duplicated('username', keep=False)]
if len(duplicates) > 0:
    print(f"\nDuplicate usernames found: {len(duplicates)}")
    print(duplicates[['username', 'email']])
