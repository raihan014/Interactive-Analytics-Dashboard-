# Online Retail Sales Dashboard

An interactive sales analytics dashboard built with **Python, Pandas, Streamlit, and Plotly** for the CodeNova Data Science Internship — Batch 01, Task 3.

The dashboard allows users to explore cleaned online retail transaction data through interactive filters, key performance indicators (KPIs), and visualizations.

## Project Overview

This project processes the UCI Online Retail dataset and presents the resulting positive-sales transactions in an interactive dashboard.

### Dashboard Features

- **Dataset overview:** View the number of processed transaction rows, countries, and distinct product stock codes.
- **Interactive filters:** Filter transactions by invoice date, country, product description, and unit price.
- **Sales KPIs:** Explore total sales value, unique orders, units sold, and average order value.
- **Interactive visualizations:** Explore sales trends, comparisons, and transaction-level relationships.
- **Product filtering:** View available product descriptions for the selected countries.
- **Empty-state handling:** Display helpful messages when no country is selected or no transactions match the filters.
- **Reset filters:** Restore the dashboard's default filter settings.
- **Copyright footer:** Display project ownership information.

## Technologies Used

- Python
- Pandas
- Streamlit
- Plotly
- OpenPyXL

## Dataset

**Source:** UCI Machine Learning Repository — Online Retail

Dataset page: https://archive.ics.uci.edu/dataset/352/online-retail

The dataset contains transactions from a UK-based online retail business between December 2010 and December 2011.

### Data Processing

The project uses a separate raw dataset and a processed dataset.

The cleaning and preparation process includes:

1. Inspecting the original dataset and its data quality.
2. Removing exact duplicate rows.
3. Excluding cancellation invoices identified by invoice numbers beginning with `C`.
4. Excluding rows with non-positive quantities or unit prices.
5. Filling missing product descriptions with `Unknown`.
6. Calculating transaction line totals using quantity multiplied by unit price.
7. Verifying the processed dataset against the project's sales rules.

Missing customer IDs are retained because customer IDs are not required for the dashboard's main analyses.

### Important Sales Metric Note

The dashboard's sales value represents the sum of positive sales transaction lines remaining after the project's cleaning rules. It should **not** be interpreted as net revenue after returns.

### Product Count Definitions

The project distinguishes between:

- **Distinct stock codes:** Unique product identifiers in the processed dataset.
- **Distinct product descriptions:** Unique readable product descriptions.

These counts may differ because product identifiers and descriptions are different fields.

## Installation and Setup

### Prerequisites

- Python 3.14.7, as used during development
- Git
- Visual Studio Code or another Python editor

### 1. Clone the repository

```bash
git clone GITHUB_REPO_URL
cd Task-3
```

Replace `GITHUB_REPO_URL` with the repository URL after creating the GitHub repository.

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Prepare the dataset

Download the Online Retail dataset from the UCI dataset page linked above.

Place the original workbook at:

```text
data/raw/Online Retail.xlsx
```

Create the required folders if they do not exist. Then generate the processed dataset using the project's preparation script:

```powershell
python prepare_data.py
```

Verify the resulting dataset:

```powershell
python verify_processed_data.py
```

### 5. Run the dashboard

```powershell
streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to explore the dashboard.

## 🚀 Live Demo

**Explore the deployed dashboard here:**

[Online Retail Sales Dashboard](https://retail-analytics-task3.streamlit.app)

The dashboard allows users to explore online retail sales data through interactive filters, key performance indicators (KPIs), and visualizations.


## Author

**Marfi Hasan Raihan**

- GitHub: https://github.com/raihan014
- Portfolio: https://sites.google.com/view/raihanmarfi/home
- LinkedIn: https://www.linkedin.com/in/marfi-hasan-raihan-8853a8283

## Acknowledgements

Dataset provided by the UCI Machine Learning Repository.

This project was developed as part of the CodeNova Data Science Internship — Batch 01.

## License and Attribution

The Online Retail dataset is provided by the UCI Machine Learning Repository. Refer to the dataset page for its citation and licensing information.

*Prepared as part of the CodeNova Data Science Internship — Batch 01, Task 3.*
