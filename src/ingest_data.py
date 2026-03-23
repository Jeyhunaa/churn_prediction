import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
FILE_PATH = r'data\E Commerce Dataset.xlsx'
DB_URL = "postgresql+psycopg2://postgres:admin@localhost:5432/postgres"
TABLE_NAME = 'ecommerce_churn'

def ingest_data():
    try:
        # 1. Load the dataset 
        # (Requires 'pip install openpyxl')
        print(f"Reading file from: {FILE_PATH}...")
        df = pd.read_excel(FILE_PATH)
        
        # 2. Normalize columns to lowercase
        # This fixes the "UndefinedColumn" error by ensuring Python and Postgres
        # both use lowercase names without double-quote restrictions.
        df.columns = [c.lower().strip() for c in df.columns]
        
        print(f"Successfully loaded {len(df)} rows.")
        print(f"Columns normalized: {df.columns.tolist()[:5]}...")

        # 3. Establish Database Connection
        engine = create_engine(DB_URL)

        # 4. Load Data into Postgres
        print(f"Ingesting data into table '{TABLE_NAME}'...")
        
        # We use 'replace' here to drop the old table that had the 
        # "case-sensitive" column issues and create a fresh one.
        df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False)
        
        print("SUCCESS: Table recreated and data successfully ingested!")

    except FileNotFoundError:
        print("ERROR: The Excel file was not found. Check your file path.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    ingest_data()