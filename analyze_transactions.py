from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/Online Retail.xlsx")

# Check whether the original dataset exists.
if not DATA_PATH.exists():
    print(f"Dataset not found: {DATA_PATH}")

else:
    # Read the original workbook without modifying it.
    df = pd.read_excel(DATA_PATH)

    # Calculate the value of each transaction line.
    df["LineTotal"] = df["Quantity"] * df["UnitPrice"]

    print("\nTransaction Overview")
    print(f"Total rows: {len(df):,}")

    # In this dataset, cancellation invoice numbers start with C.
    cancellations = df["InvoiceNo"].astype(str).str.startswith("C")
    print(f"Cancellation rows: {cancellations.sum():,}")
    print(f"Other invoice rows: {(~cancellations).sum():,}")

    # Investigate quantities and prices without deleting rows.
    print(f"\nRows with Quantity <= 0: {(df['Quantity'] <= 0).sum():,}")
    print(f"Rows with UnitPrice <= 0: {(df['UnitPrice'] <= 0).sum():,}")

    print("\nLine Total Summary")
    print(df["LineTotal"].describe())

    print("\nCancellation Transactions")
    print(
        df.loc[cancellations, [
            "InvoiceNo", "StockCode", "Quantity",
            "UnitPrice", "InvoiceDate"
        ]].head(10).to_string(index=False)
    )

    print("\nCountry Overview")
    print(f"Unique countries: {df['Country'].nunique():,}")
    print("Top 10 countries by transaction rows:")
    print(df["Country"].value_counts().head(10).to_string())

    # Investigate exact duplicate rows.
    print("\nDuplicate Row Overview")

    duplicate_mask = df.duplicated(keep=False)
    duplicate_rows = df.loc[duplicate_mask]

    print(f"Rows belonging to duplicate groups: {len(duplicate_rows):,}")

    print("\nFirst 10 duplicate-row examples:")
    print(
        duplicate_rows.sort_values(
            by=["InvoiceNo", "StockCode", "InvoiceDate"]
        ).head(10).to_string(index=False)
    )

    print("\nDuplicate counts for selected columns:")
    print(
        df.duplicated(
            subset=["InvoiceNo", "StockCode", "Quantity", "UnitPrice"],
            keep=False
        ).sum()
    )
