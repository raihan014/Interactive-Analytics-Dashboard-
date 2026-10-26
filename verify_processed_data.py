from pathlib import Path
import pandas as pd

# Find the project folder and processed dataset
PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "processed" / "online_retail_sales.csv"

# Check whether the dataset exists
if not DATA_PATH.exists():
    print(f"ERROR: File not found: {DATA_PATH}")
else:
    # Load the dataset with the correct data types
    df = pd.read_csv(
        DATA_PATH,
        dtype={"InvoiceNo": "string", "StockCode": "string"},
        parse_dates=["InvoiceDate"],
        low_memory=False,
    )

    print("\nProcessed Data Verification")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Duplicate rows: {df.duplicated().sum():,}")
    print(f"Missing values by column:\n{df.isna().sum().to_string()}")

    print("\nSales Rule Checks")
    print(
        "Cancellation invoices remaining:",
        df["InvoiceNo"].str.startswith("C").sum(),
    )
    print("Non-positive quantities:", (df["Quantity"] <= 0).sum())
    print("Non-positive unit prices:", (df["UnitPrice"] <= 0).sum())
    print("Non-positive line totals:", (df["LineTotal"] <= 0).sum())

    print("\nData Range")
    print(f"Earliest: {df['InvoiceDate'].min()}")
    print(f"Latest: {df['InvoiceDate'].max()}")

    print("\nSales Summary")
    print(f"Total sales value: {df['LineTotal'].sum():,.2f}")
    print(f"Unique invoices: {df['InvoiceNo'].nunique():,}")
    print(f"Unique countries: {df['Country'].nunique():,}")
    print(f"Unique products: {df['StockCode'].nunique():,}")

    print("\nVerification complete.")
