from pathlib import Path
import base64
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. PAGE CONFIGURATION

st.set_page_config(
    page_title="Online Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "processed" / "online_retail_sales.csv"

OWNER_NAME = "Marfi Hasan Raihan"
COPYRIGHT_YEAR = 2026

# 2. LOAD AND VALIDATE THE DATASET

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """Load the processed dataset and validate its essential columns."""

    data = pd.read_csv(
        file_path,
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string",
            "Country": "string",
            "Description": "string",
        },
        parse_dates=["InvoiceDate"],
        low_memory=False,
    )

    required_columns = {
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "LineTotal",
        "Country",
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    data["Description"] = (
        data["Description"]
        .fillna("Unknown product")
        .astype("string")
        .str.strip()
        .replace("", "Unknown product")
    )

    data["Country"] = (
        data["Country"]
        .fillna("Unknown country")
        .astype("string")
    )

    for column in ["Quantity", "UnitPrice", "LineTotal"]:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        )

    data = data.dropna(
        subset=[
            "InvoiceNo",
            "StockCode",
            "Description",
            "Country",
            "InvoiceDate",
            "Quantity",
            "UnitPrice",
            "LineTotal",
        ]
    ).copy()

    # This dashboard analyses positive sales lines.
    # It does not calculate net revenue after returns.
    data = data[
        (data["Quantity"] > 0)
        & (data["UnitPrice"] > 0)
        & (data["LineTotal"] > 0)
    ].copy()

    return data


if not DATA_PATH.exists():
    st.error(
        "The processed dataset was not found.\n\n"
        "Expected file: "
        "`data/processed/online_retail_sales.csv`"
    )
    st.stop()

try:
    df = load_data(str(DATA_PATH))
except Exception as exc:
    st.error(
        "The dataset could not be loaded. "
        "Please check the CSV file and its column names."
    )
    st.exception(exc)
    st.stop()

if df.empty:
    st.error("The processed dataset contains no usable sales transactions.")
    st.stop()


# 3. DATASET INFORMATION

countries = sorted(
    df["Country"].dropna().astype(str).unique().tolist()
)

min_date = df["InvoiceDate"].min().date()
max_date = df["InvoiceDate"].max().date()

min_price = float(df["UnitPrice"].min())
max_price = float(df["UnitPrice"].max())

# Use product descriptions for readable product.
all_product_descriptions = sorted(
    df["Description"].dropna().astype(str).unique().tolist()
)

# measurements:
# StockCode = distinct product identifiers.
# Description = distinct readable product names.
unique_stock_codes = int(df["StockCode"].nunique())
unique_descriptions = int(df["Description"].nunique())

# 4. INITIALISE FILTER STATE

# Empty lists are used for country and product filters to avoid selecting all options by default.
# Users must choose the countries they want to analyse.

if "date_filter" not in st.session_state:
    st.session_state["date_filter"] = (min_date, max_date)

if "country_filter" not in st.session_state:
    st.session_state["country_filter"] = []

if "product_filter" not in st.session_state:
    st.session_state["product_filter"] = []

if "price_filter" not in st.session_state:
    st.session_state["price_filter"] = (min_price, max_price)

def reset_filters():
    """Reset all filters without selecting every country."""

    st.session_state["date_filter"] = (min_date, max_date)
    st.session_state["country_filter"] = []
    st.session_state["product_filter"] = []
    st.session_state["price_filter"] = (min_price, max_price)

def sync_products_to_countries():
    """Keep only product descriptions available in the chosen countries."""

    chosen_countries = st.session_state.get("country_filter", [])

    if not chosen_countries:
        st.session_state["product_filter"] = []
        return

    available_products = set(
        df.loc[
            df["Country"].isin(chosen_countries),
            "Description",
        ]
        .dropna()
        .astype(str)
        .unique()
    )

    current_products = st.session_state.get("product_filter", [])

    st.session_state["product_filter"] = [
        product
        for product in current_products
        if product in available_products
    ]

# 5. SIDEBAR FILTERS

with st.sidebar:
    st.title("🔎 Sales Filters")
    st.caption("Change the filters to explore the data.")

    st.date_input(
        "Invoice date range",
        min_value=min_date,
        max_value=max_date,
        key="date_filter",
        help="Choose the start and end dates for the analysis.",
    )

    st.multiselect(
        "Countries",
        options=countries,
        key="country_filter",
        on_change=sync_products_to_countries,
        placeholder="Choose one or more countries",
        help=(
            "Select one or more countries."
        ),
    )

    selected_countries = st.session_state["country_filter"]

    st.caption(
        f"{len(selected_countries):,} of {len(countries):,} "
        "countries selected"
    )

    # Only show products sold in the selected countries.
    if selected_countries:
        country_product_df = df[
            df["Country"].isin(selected_countries)
        ]

        country_products = sorted(
            country_product_df["Description"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        country_unique_codes = int(
            country_product_df["StockCode"].nunique()
        )

        st.multiselect(
            "Products",
            options=country_products,
            key="product_filter",
            placeholder="Search product descriptions",
            help=(
                "Search by readable product description. "
                "Leave the selection empty to include all available products."
            ),
        )

        selected_products = st.session_state["product_filter"]

        st.caption(
            f"{len(selected_products):,} of {len(country_products):,} "
            "available product descriptions selected"
        )

        st.caption(
            "Distinct product codes in selected countries: "
            f"{country_unique_codes:,}"
        )

    else:
        # Disable product selection until a country is chosen.
        # Do not display a second informational message in the sidebar.
        st.multiselect(
            "Products",
            options=[],
            key="product_filter",
            disabled=True,
            placeholder="Select a country first",
            help="Select at least one country to see its products.",
        )

        st.caption(
            f"0 of {len(all_product_descriptions):,} "
            "product descriptions selected"
        )

    st.slider(
        "Unit price range (£)",
        min_value=min_price,
        max_value=max_price,
        key="price_filter",
        format="£%.2f",
        help="Filter transactions by unit price.",
    )

    st.divider()

    st.button(
        "↩️ Reset filters",
        on_click=reset_filters,
        use_container_width=True,
    )

# 6. FOOTER

def show_footer():
    """Display the dashboard footer."""

    st.divider()

    st.markdown(
        f"""
        <div style="text-align:center; padding:12px 0 4px 0;">
            <p style="margin-bottom:6px;">
                © {COPYRIGHT_YEAR}
                <strong>{OWNER_NAME}</strong>. All rights reserved.
            </p>
            <p style="font-size:0.85rem; color:#999999;">
                Online Retail Sales Dashboard |
                Built with Python, Streamlit, Pandas and Plotly
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 7. DASHBOARD HEADER

LOGO_PATH = PROJECT_DIR / "assets" / "shopping cart.jpg"

st.markdown(
    """
    <style>
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 12px;
    }

    .dashboard-logo {
        width: 76px;
        height: 76px;
        object-fit: contain;
        flex-shrink: 0;
    }

    .dashboard-title {
        font-size: clamp(1.8rem, 3vw, 2.8rem);
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
        padding: 0;
    }

    @media (max-width: 600px) {
        .dashboard-header {
            gap: 10px;
        }

        .dashboard-logo {
            width: 52px;
            height: 52px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if LOGO_PATH.is_file():
    logo_base64 = base64.b64encode(
        LOGO_PATH.read_bytes()
    ).decode("utf-8")

    st.markdown(
        f"""
        <div class="dashboard-header">
            <img
                class="dashboard-logo"
                src="data:image/jpeg;base64,{logo_base64}"
                alt="Online retail shopping cart logo"
            />
            <h1 class="dashboard-title">
                Online Retail Sales Dashboard
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.title("Online Retail Sales Dashboard")
    st.warning(
        "Dashboard logo not found. "
        "Please check the assets/shopping cart.jpg file."
    )

st.markdown(
    "Explore online retail transactions through interactive filters, "
    "key performance indicators, and visual analytics."
)


# 8. DATASET OVERVIEW ALWAYS VISIBLE

st.subheader("📁 Dataset Overview")

overview1, overview2, overview3 = st.columns(3)

with overview1:
    st.metric(
        "Transaction Rows",
        f"{len(df):,}",
    )

with overview2:
    st.metric(
        "Countries",
        f"{df['Country'].nunique():,}",
    )

with overview3:
    st.metric(
        "Unique Products (Stock Codes)",
        f"{unique_stock_codes:,}",
        help=(
            "This counts distinct StockCode identifiers. "
            f"The dataset has {unique_descriptions:,} distinct product "
            "descriptions."
        ),
    )

st.caption(
    f"The processed dataset contains {unique_stock_codes:,} distinct "
    f"stock codes and {unique_descriptions:,} distinct product descriptions. "
    "Product descriptions are used as readable filter labels."
)

st.divider()


# 9. CHECK FILTERS

selected_dates = st.session_state["date_filter"]
selected_countries = st.session_state["country_filter"]
selected_products = st.session_state["product_filter"]
selected_prices = st.session_state["price_filter"]


# Show a message in the main page when no country is selected.
# Keep Dataset Overview visible only, and do not show charts or KPIs

if not selected_countries:
    st.info(
        "No country is selected. Choose at least one country "
        "from the sidebar to view sales performance. "
        "Your dataset is still loaded."
    )

    show_footer()
    st.stop()


# Make sure the user has selected both dates.
if (
    not isinstance(selected_dates, (tuple, list))
    or len(selected_dates) != 2
    or selected_dates[0] is None
    or selected_dates[1] is None
):
    st.info("Choose both a start date and an end date to display sales results.")
    show_footer()
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    st.warning("The start date must be earlier than or equal to the end date.")
    show_footer()
    st.stop()

# 10. APPLY FILTERS

filtered_df = df[
    (df["InvoiceDate"].dt.date >= start_date)
    & (df["InvoiceDate"].dt.date <= end_date)
    & (df["Country"].isin(selected_countries))
].copy()

# A product filter only narrows the data when products are selected.
if selected_products:
    filtered_df = filtered_df[
        filtered_df["Description"].isin(selected_products)
    ].copy()

price_low, price_high = selected_prices

filtered_df = filtered_df[
    (filtered_df["UnitPrice"] >= price_low)
    & (filtered_df["UnitPrice"] <= price_high)
].copy()

# 11. HANDLE EMPTY FILTER RESULTS

if filtered_df.empty:
    st.warning(
        "No transactions match your current filters. "
        "Try another product, country, date range, or unit price range."
    )

    st.caption(
        "The dataset is still loaded. Change your sidebar filters "
        "or click Reset filters to start again."
    )

    show_footer()
    st.stop()

# 12. SALES PERFORMANCE KPIs

st.subheader("📈 Sales Performance")

total_sales = float(filtered_df["LineTotal"].sum())

unique_orders = int(filtered_df["InvoiceNo"].nunique())

units_sold = float(filtered_df["Quantity"].sum())

average_order_value = (
    total_sales / unique_orders
    if unique_orders > 0
    else 0.0
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Sales Value",
        f"£{total_sales:,.2f}",
    )

with kpi2:
    st.metric(
        "Unique Orders",
        f"{unique_orders:,}",
    )

with kpi3:
    st.metric(
        "Units Sold",
        f"{units_sold:,.0f}",
    )

with kpi4:
    st.metric(
        "Average Order Value",
        f"£{average_order_value:,.2f}",
    )

st.caption(
    "Sales value is the sum of positive sales lines remaining after "
    "the project's cleaning steps. It is not net revenue after returns."
)

st.divider()

# 13. SALES TREND OVER TIME

st.subheader("📅 Sales Trend Over Time")

daily_sales = (
    filtered_df.assign(
        SalesDate=filtered_df["InvoiceDate"].dt.date
    )
    .groupby("SalesDate", as_index=False)["LineTotal"]
    .sum()
    .rename(
        columns={
            "SalesDate": "Date",
            "LineTotal": "Sales Value",
        }
    )
)

if not daily_sales.empty:
    line_chart = px.line(
        daily_sales,
        x="Date",
        y="Sales Value",
        markers=True,
        title="Daily Sales Value",
        labels={
            "Date": "Invoice Date",
            "Sales Value": "Sales Value (£)",
        },
    )

    line_chart.update_layout(hovermode="x unified")

    st.plotly_chart(
        line_chart,
        use_container_width=True,
    )

st.divider()

# 14. SALES BY COUNTRY

st.subheader("🌍 Sales by Country")

country_sales = (
    filtered_df.groupby("Country", as_index=False)["LineTotal"]
    .sum()
    .rename(
        columns={
            "LineTotal": "Sales Value",
        }
    )
    .sort_values("Sales Value", ascending=False)
    .head(15)
)

if not country_sales.empty:
    country_chart = px.bar(
        country_sales.sort_values("Sales Value"),
        x="Sales Value",
        y="Country",
        orientation="h",
        title="Top Countries by Sales Value (up to 15)",
        labels={
            "Sales Value": "Sales Value (£)",
            "Country": "Country",
        },
        text_auto=".2s",
    )

    st.plotly_chart(
        country_chart,
        use_container_width=True,
    )

st.divider()

# 15. TOP PRODUCTS BY SALES VALUE

st.subheader("🛍️ Top Products by Sales Value")

product_sales = (
    filtered_df.groupby("Description", as_index=False)["LineTotal"]
    .sum()
    .rename(
        columns={
            "LineTotal": "Sales Value",
        }
    )
    .sort_values("Sales Value", ascending=False)
    .head(10)
)

if not product_sales.empty:
    product_chart = px.bar(
        product_sales.sort_values("Sales Value"),
        x="Sales Value",
        y="Description",
        orientation="h",
        title="Top 10 Product Descriptions by Sales Value",
        labels={
            "Sales Value": "Sales Value (£)",
            "Description": "Product Description",
        },
        text_auto=".2s",
    )

    st.plotly_chart(
        product_chart,
        use_container_width=True,
    )

st.divider()

# 16. QUANTITY VS SALES VALUE

st.subheader("🔬 Quantity vs. Sales Value")

st.caption(
    "Each point represents a transaction line. Hover over a point "
    "to inspect its values. For responsiveness, at most 10,000 "
    "transaction lines are sampled for this chart."
)

scatter_df = filtered_df

if len(scatter_df) > 10_000:
    scatter_df = scatter_df.sample(
        n=10_000,
        random_state=42,
    )

scatter_chart = px.scatter(
    scatter_df,
    x="Quantity",
    y="LineTotal",
    color="Country",
    hover_data=[
        "Description",
        "InvoiceNo",
        "UnitPrice",
        "InvoiceDate",
    ],
    title="Transaction Quantity vs. Sales Value",
    labels={
        "Quantity": "Quantity",
        "LineTotal": "Sales Value (£)",
        "Country": "Country",
    },
    opacity=0.65,
)

st.plotly_chart(
    scatter_chart,
    use_container_width=True,
)

st.divider()


# 17. FILTERED TRANSACTION TABLE AND CSV DOWNLOAD

st.subheader("📋 Filtered Transaction Data")

st.write(
    f"Matching transaction rows: **{len(filtered_df):,}**"
)

display_columns = [
    "InvoiceNo",
    "InvoiceDate",
    "StockCode",
    "Description",
    "Quantity",
    "UnitPrice",
    "LineTotal",
    "Country",
]

with st.expander("View transaction records"):
    st.dataframe(
        filtered_df[display_columns].sort_values(
            "InvoiceDate",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_df[display_columns].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download filtered transactions as CSV",
        data=csv_data,
        file_name="filtered_online_retail_sales.csv",
        mime="text/csv",
    )

st.caption(
    "Dataset source: UCI Online Retail. This dashboard uses "
    "the project's cleaned and processed dataset."
)

# 18. DISPLAY FOOTER

show_footer()
