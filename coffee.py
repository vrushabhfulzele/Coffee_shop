import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


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

    /* Main title */
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

    /* KPI cards */
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

    /* Section headings */
    .section-title {
        font-size: 23px;
        font-weight: 700;
        color: #4B2E20;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #3E2723;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("../Datasets/CoffeeShopSales-cleaned.csv")

    # Convert date
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    # Month
    df["Month"] = df["transaction_date"].dt.strftime("%B")

    # Month number for correct sorting
    df["Month_Number"] = df["transaction_date"].dt.month

    return df


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("☕ Coffee Dashboard")

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Filters")


# Store filter
stores = ["All Stores"] + sorted(
    df["store_location"].dropna().unique().tolist()
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
    ]


# Category filter
categories = ["All Categories"] + sorted(
    filtered_df["product_category"].dropna().unique().tolist()
)

selected_category = st.sidebar.selectbox(
    "☕ Select Category",
    categories
)


if selected_category != "All Categories":

    filtered_df = filtered_df[
        filtered_df["product_category"] == selected_category
    ]


# Date filter
min_date = df["transaction_date"].min()
max_date = df["transaction_date"].max()

selected_dates = st.sidebar.date_input(
    "📅 Date Range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date()
)


if len(selected_dates) == 2:

    start_date = pd.to_datetime(selected_dates[0])
    end_date = pd.to_datetime(selected_dates[1])

    filtered_df = filtered_df[
        (filtered_df["transaction_date"] >= start_date)
        &
        (filtered_df["transaction_date"] <= end_date)
    ]


# Reset information
st.sidebar.markdown("---")

st.sidebar.info(
    "Use the filters above to explore sales "
    "by store, category and date."
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">☕ Coffee Shop Sales Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Explore sales performance, product trends and customer demand'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_sales = filtered_df["total_amount"].sum()

total_transactions = filtered_df["transaction_id"].nunique()

total_quantity = filtered_df["transaction_qty"].sum()

average_order_value = (
    total_sales / total_transactions
    if total_transactions > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 TOTAL SALES</div>
            <div class="kpi-value">₹{total_sales:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🧾 TRANSACTIONS</div>
            <div class="kpi-value">{total_transactions:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">☕ ITEMS SOLD</div>
            <div class="kpi-value">{total_quantity:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💵 AVG ORDER VALUE</div>
            <div class="kpi-value">₹{average_order_value:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# SALES OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📈 Sales Overview</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Monthly Sales
# ------------------------------------------------------------

with col1:

    monthly_sales = (
        filtered_df
        .groupby(["Month_Number", "Month"])["total_amount"]
        .sum()
        .reset_index()
        .sort_values("Month_Number")
    )

    fig_month = px.line(
        monthly_sales,
        x="Month",
        y="total_amount",
        markers=True,
        title="Monthly Sales Trend",
        labels={
            "total_amount": "Sales (₹)",
            "Month": "Month"
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
# Store Sales
# ------------------------------------------------------------

with col2:

    store_sales = (
        filtered_df
        .groupby("store_location")["total_amount"]
        .sum()
        .reset_index()
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
            "total_amount": "Sales (₹)",
            "store_location": "Store"
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
    '<div class="section-title">☕ Product Analysis</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# Category Sales
# ------------------------------------------------------------

with col1:

    category_sales = (
        filtered_df
        .groupby("product_category")["total_amount"]
        .sum()
        .reset_index()
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
            "total_amount": "Sales (₹)",
            "product_category": "Category"
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
# Top Product Types
# ------------------------------------------------------------

with col2:

    top_products = (
        filtered_df
        .groupby("product_type")["transaction_qty"]
        .sum()
        .nlargest(10)
        .reset_index()
    )

    fig_products = px.bar(
        top_products,
        x="transaction_qty",
        y="product_type",
        orientation="h",
        title="Top 10 Products by Quantity Sold",
        text_auto=True,
        labels={
            "transaction_qty": "Quantity Sold",
            "product_type": "Product"
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
    '<div class="section-title">📅 Weekday Performance</div>',
    unsafe_allow_html=True
)


weekday_sales = (
    filtered_df
    .groupby("weekday")["total_amount"]
    .mean()
    .reset_index()
)


# Keep normal weekday order
weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_sales["weekday"] = pd.Categorical(
    weekday_sales["weekday"],
    categories=weekday_order,
    ordered=True
)

weekday_sales = weekday_sales.sort_values("weekday")


fig_weekday = px.bar(
    weekday_sales,
    x="weekday",
    y="total_amount",
    title="Average Sales by Weekday",
    text_auto=".2s",
    labels={
        "total_amount": "Average Sales (₹)",
        "weekday": "Day"
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
# STORE + CATEGORY + PRODUCT EXPLORER
# ============================================================

st.markdown(
    '<div class="section-title">🔎 Product Explorer</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    explorer_store = st.selectbox(
        "🏪 Choose Store",
        sorted(df["store_location"].unique()),
        key="explorer_store"
    )


explorer_df = df[
    df["store_location"] == explorer_store
]


with col2:

    explorer_category = st.selectbox(
        "☕ Choose Category",
        sorted(
            explorer_df["product_category"].unique()
        ),
        key="explorer_category"
    )


product_df = explorer_df[
    explorer_df["product_category"] ==
    explorer_category
]


product_sales = (
    product_df
    .groupby("product_type")["total_amount"]
    .sum()
    .reset_index()
    .sort_values(
        "total_amount",
        ascending=False
    )
)


fig_product_explorer = px.bar(
    product_sales,
    x="product_type",
    y="total_amount",
    title=f"{explorer_category} Sales at {explorer_store}",
    text_auto=".2s",
    labels={
        "product_type": "Product",
        "total_amount": "Sales (₹)"
    }
)

fig_product_explorer.update_layout(
    template="plotly_white",
    height=450,
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_product_explorer,
    use_container_width=True
)


# ============================================================
# PIVOT TABLE
# ============================================================

st.markdown(
    '<div class="section-title">📊 Category vs Store</div>',
    unsafe_allow_html=True
)


pivot_table = pd.pivot_table(
    df,
    index="product_category",
    columns="store_location",
    values="total_amount",
    aggfunc="sum",
    margins=True
)

st.dataframe(
    pivot_table.style.format("₹{:,.0f}"),
    use_container_width=True
)


# ============================================================
# RAW DATA
# ============================================================

with st.expander("📋 View Transaction Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#777;">
        ☕ Coffee Shop Sales Analytics Dashboard
        <br>
        Built with Python • Pandas • Streamlit • Plotly
    </div>
    """,
    unsafe_allow_html=True
)
