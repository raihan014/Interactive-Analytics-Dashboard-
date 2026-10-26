from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/Online Retail.xlsx")
OUTPUT_DIR = Path("data/processed")
OUTPUT_PATH = OUTPUT_DIR / "online_retail_sales.csv"

# Check whether the original dataset exists.
if not RAW_PATH.exists():
    print(f"Dataset not found: {RAW_PATH}")

else:
    # Read the original workbook without modifying it.
    df = pd.read_excel(RAW_PATH)

    original_rows = len(df)
    original_duplicates = int(df.duplicated().sum())

    # Remove exact duplicate records.
    df = df.drop_duplicates().copy()
    rows_after_deduplication = len(df)

    # Exclude cancellation invoices.
    is_cancellation = df["InvoiceNo"].astype(str).str.startswith("C")
    cancellation_rows = int(is_cancellation.sum())
    df = df.loc[~is_cancellation].copy()

    # Keep positive-quantity, positive-price sales only.
    invalid_sales = (df["Quantity"] <= 0) | (df["UnitPrice"] <= 0)
    non_positive_rows = int(invalid_sales.sum())
    df = df.loc[~invalid_sales].copy()

    # Make missing product descriptions readable in charts.
    df["Description"] = df["Description"].fillna("Unknown")

    # Calculate the value of each sales line.
    df["LineTotal"] = df["Quantity"] * df["UnitPrice"]

    # Create the output folder if it doesn't exist.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save the processed data separately from the raw workbook.
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nData Processing Summary")
    print(f"Original rows: {original_rows:,}")
    print(f"Exact duplicate rows removed: {original_duplicates:,}")
    print(f"Rows after deduplication: {rows_after_deduplication:,}")
    print(f"Cancellation rows excluded: {cancellation_rows:,}")
    print(f"Non-positive sales rows excluded: {non_positive_rows:,}")
    print(f"Final processed rows: {len(df):,}")
    print(f"Missing customer IDs retained: {df['CustomerID'].isna().sum():,}")
    print(f"Missing descriptions remaining: {df['Description'].isna().sum():,}")
    print(f"Non-positive line totals remaining: {(df['LineTotal'] <= 0).sum():,}")
    print(f"Saved processed data to: {OUTPUT_PATH}")
