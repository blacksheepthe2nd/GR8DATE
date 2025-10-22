import psycopg2

print("🔍 Discovering your database structure...")

try:
    # Use the external database URL
    conn = psycopg2.connect(
        "postgresql://gr8date_db_user:sCi0RdhIVnrwLKfvlpGtNxfjfbTfU4M8@dpg-d3rkubripnbc73eo08k0-a.oregon-postgres.render.com/gr8date_db"
    )
    
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    tables = cursor.fetchall()
    print(f"✅ Found {len(tables)} tables:")
    
    for table in tables:
        table_name = table[0]
        print(f"\n📊 Table: {table_name}")
        
        # Get columns for this table
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]} ({col[1]})")
            
        # Show first few rows to understand data
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample_row = cursor.fetchone()
            if sample_row:
                print(f"   📝 Sample data: {sample_row}")
        except:
            print(f"   📝 Could not fetch sample data")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
