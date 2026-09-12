import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Coffee Shop Sales Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #F8F9FA;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.dashboard-title {
    font-size: 38px;
    font-weight: 700;
    color: #4B2E20;
    margin-bottom: 0px;
}

.dashboard-subtitle {
    font-size: 17px;
    color: #6C757D;
    margin-bottom: 25px;
}

.kpi-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #8B5E3C;
}

.kpi-title {
    color: #6C757D;
    font-size: 14px;
    font-weight: 600;
}

.kpi-value {
    color: #4B2E20;
    font-size: 27px;
    font-weight: 700;
    margin-top: 5px;
}

.section-title {
    font-size: 23px;
    font-weight: 700;
    color: #4B2E20;
    margin-top: 20px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FIND DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

possible_paths = [
    BASE_DIR / "Datasets" / "CoffeeShopSales-cleaned.csv",
    BASE_DIR / "datasets" / "CoffeeShopSales-cleaned.csv",
    BASE_DIR / "CoffeeShopSales-cleaned.csv",
    BASE_DIR.parent / "Datasets" / "CoffeeShopSales-cleaned.csv"
]

DATA_FILE = None

for path in possible_paths:
    if path.exists():
        DATA_FILE = path
        break


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(file_path):

    data = pd.read_csv(file_path)

    # Remove unnecessary unnamed columns if present
    unnamed_columns = [
        col for col in data.columns
        if col.lower().startswith("unnamed")
    ]

    if unnamed_columns:
        data = data.drop(columns=unnamed_columns)

    # Convert transaction date
    if "transaction_date" in data.columns:

        data["transaction_date"] = pd.to_datetime(
            data["transaction_date"],
            errors="coerce"
        )

        # Month name
        data["Month"] = data["transaction_date"].dt.strftime("%B")

        # Month number for correct sorting
        data["Month_Number"] = (
            data["transaction_date"].dt.month
        )

    return data


# ============================================================
# DATA FILE ERROR HANDLING
# ============================================================

if DATA_FILE is None:

    st.error(
        "❌ CoffeeShopSales-cleaned.csv was not found."
    )

    st.markdown("""
    ### Please check your GitHub repository structure

    Your repository should look like this:

    ```
    coffee_shop/
    │
    ├── coffee.py
    ├── requirements.txt
    │
    └── Datasets/
        └── CoffeeShopSales-cleaned.csv
    ```

    **Important:**
    - The folder name should be `Datasets`
    - The CSV should be named exactly:
      `CoffeeShopSales-cleaned.csv`
    - Make sure the CSV is committed and pushed to GitHub.
    """)

    st.stop()


# Load dataset
df = load_data(str(DATA_FILE))


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "transaction_date",
    "store_location",
    "product_category",
    "product_type",
    "transaction_qty",
    "total_amount"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "❌ Required columns are missing from the dataset."
    )

    st.write("Missing columns:")

    st.write(missing_columns)

    st.write("Available columns:")

    st.write(df.columns.tolist())

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("☕ Coffee Dashboard")

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Filters")


# Store filter
stores = ["All Stores"] + sorted(
    df["store_location"]
    .dropna()
    .unique()
    .tolist()
)

selected_store = st.sidebar.selectbox(
    "🏪 Select Store",
    stores
)


# Apply store filter
if selected_store == "All Stores":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["store_location"] == selected_store
    ].copy()


# Category filter
categories = ["All Categories"] + sorted(
    filtered_df["product_category"]
    .dropna()
    .unique()
    .tolist()
)

selected_category = st.sidebar.selectbox(
    "☕ Select Category",
    categories
)


if selected_category != "All Categories":

    filtered_df = filtered_df[
        filtered_df["product_category"]
        == selected_category
    ].copy()


# Date filter
min_date = df["transaction_date"].min()
max_date = df["transaction_date"].max()


if pd.notna(min_date) and pd.notna(max_date):

    selected_dates = st.sidebar.date_input(
        "📅 Date Range",
        value=(
            min_date.date(),
            max_date.date()
        ),
        min_value=min_date.date(),
        max_value=max_date.date()
    )

    if len(selected_dates) == 2:

        start_date = pd.to_datetime(
            selected_dates[0]
        )

        end_date = (
            pd.to_datetime(selected_dates[1])
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )

        filtered_df = filtered_df[
            (
                filtered_df["transaction_date"]
                >= start_date
            )
            &
            (
                filtered_df["transaction_date"]
                <= end_date
            )
        ].copy()


st.sidebar.markdown("---")

st.sidebar.info(
    "Use the filters above to explore "
    "coffee shop sales."
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '☕ Coffee Shop Sales Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Analyze sales, products, stores and customer demand'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_df["total_amount"].sum()

total_quantity = filtered_df["transaction_qty"].sum()

total_transactions = len(filtered_df)

if total_transactions > 0:

    average_transaction = (
        total_sales / total_transactions
    )

else:

    average_transaction = 0


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                💰 TOTAL SALES
            </div>
            <div class="kpi-value">
                ₹{total_sales:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                🧾 TRANSACTIONS
            </div>
            <div class="kpi-value">
                {total_transactions:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                ☕ ITEMS SOLD
            </div>
            <div class="kpi-value">
                {total_quantity:,}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">
                💵 AVG TRANSACTION
            </div>
            <div class="kpi-value">
                ₹{average_transaction:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SALES OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📈 Sales Overview'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# MONTHLY SALES
# ------------------------------------------------------------

with col1:

    monthly_sales = (
        filtered_df
        .groupby(
            ["Month_Number", "Month"],
            as_index=False
        )["total_amount"]
        .sum()
        .sort_values("Month_Number")
    )

    fig_month = px.line(
        monthly_sales,
        x="Month",
        y="total_amount",
        markers=True,
        title="Monthly Sales Trend",
        labels={
            "Month": "Month",
            "total_amount": "Sales (₹)"
        }
    )

    fig_month.update_layout(
        template="plotly_white",
        height=400,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_month,
        use_container_width=True
    )


# ------------------------------------------------------------
# STORE SALES
# ------------------------------------------------------------

with col2:

    store_sales = (
        filtered_df
        .groupby(
            "store_location",
            as_index=False
        )["total_amount"]
        .sum()
        .sort_values(
            "total_amount",
            ascending=False
        )
    )

    fig_store = px.bar(
        store_sales,
        x="store_location",
        y="total_amount",
        title="Sales by Store",
        text_auto=".2s",
        labels={
            "store_location": "Store",
            "total_amount": "Sales (₹)"
        }
    )

    fig_store.update_layout(
        template="plotly_white",
        height=400
    )

    st.plotly_chart(
        fig_store,
        use_container_width=True
    )


# ============================================================
# PRODUCT ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '☕ Product Analysis'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# CATEGORY SALES
# ------------------------------------------------------------

with col1:

    category_sales = (
        filtered_df
        .groupby(
            "product_category",
            as_index=False
        )["total_amount"]
        .sum()
        .sort_values(
            "total_amount",
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x="total_amount",
        y="product_category",
        orientation="h",
        title="Sales by Product Category",
        text_auto=".2s",
        labels={
            "product_category": "Category",
            "total_amount": "Sales (₹)"
        }
    )

    fig_category.update_layout(
        template="plotly_white",
        height=450
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ------------------------------------------------------------
# TOP 10 PRODUCTS
# ------------------------------------------------------------

with col2:

    top_products = (
        filtered_df
        .groupby(
            "product_type",
            as_index=False
        )["transaction_qty"]
        .sum()
        .sort_values(
            "transaction_qty",
            ascending=False
        )
        .head(10)
    )

    fig_products = px.bar(
        top_products,
        x="transaction_qty",
        y="product_type",
        orientation="h",
        title="Top 10 Products by Quantity Sold",
        text_auto=True,
        labels={
            "product_type": "Product",
            "transaction_qty": "Quantity Sold"
        }
    )

    fig_products.update_layout(
        template="plotly_white",
        height=450
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


# ============================================================
# WEEKDAY ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📅 Weekday Performance'
    '</div>',
    unsafe_allow_html=True
)


weekday_sales = (
    filtered_df
    .groupby(
        "weekday",
        as_index=False
    )["total_amount"]
    .mean()
)


weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


if "weekday" in filtered_df.columns:

    weekday_sales["weekday"] = pd.Categorical(
        weekday_sales["weekday"],
        categories=weekday_order,
        ordered=True
    )

    weekday_sales = (
        weekday_sales
        .sort_values("weekday")
    )


fig_weekday = px.bar(
    weekday_sales,
    x="weekday",
    y="total_amount",
    title="Average Sales by Weekday",
    text_auto=".2s",
    labels={
        "weekday": "Day",
        "total_amount": "Average Sales (₹)"
    }
)

fig_weekday.update_layout(
    template="plotly_white",
    height=400
)

st.plotly_chart(
    fig_weekday,
    use_container_width=True
)


# ============================================================
# PRODUCT EXPLORER
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🔎 Product Explorer'
    '</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    explorer_store = st.selectbox(
        "🏪 Choose Store",
        sorted(
            df["store_location"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="explorer_store"
    )


explorer_df = df[
    df["store_location"] == explorer_store
].copy()


with col2:

    explorer_category = st.selectbox(
        "☕ Choose Category",
        sorted(
            explorer_df["product_category"]
            .dropna()
            .unique()
            .tolist()
        ),
        key="explorer_category"
    )


product_df = explorer_df[
    explorer_df["product_category"]
    == explorer_category
].copy()


product_sales = (
    product_df
    .groupby(
        "product_type",
        as_index=False
    )["total_amount"]
    .sum()
    .sort_values(
        "total_amount",
        ascending=False
    )
)


fig_product_explorer = px.bar(
    product_sales,
    x="product_type",
    y="total_amount",
    title=(
        f"{explorer_category} Sales - "
        f"{explorer_store}"
    ),
    text_auto=".2s",
    labels={
        "product_type": "Product",
        "total_amount": "Sales (_
````
