from pathlib import Path
import pandas as pd

# Locate the original dataset.
DATA_PATH = Path("data/raw/Online Retail.xlsx")

# Stop with a clear message if the file is missing.
if not DATA_PATH.exists():
    print(f"Dataset not found: {DATA_PATH}")

else:
    # Read the Excel workbook without modifying the original file.
    df = pd.read_excel(DATA_PATH)

    print("\nDataset Overview")
    print(f"File: {DATA_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn Names")
    print(df.columns.tolist())

    print("\nFirst 5 Rows")
    print(df.head())

    print("\nData Types")
    print(df.dtypes)

    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicate Rows")
    print(df.duplicated().sum())

    print("\nDate Information")
    if "InvoiceDate" in df.columns:
        dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
        print(f"Earliest date: {dates.min()}")
        print(f"Latest date: {dates.max()}")
        print(f"Invalid dates: {dates.isna().sum()}")

    print("\nNumerical Summary")
    print(df.describe().to_string())
