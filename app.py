from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Live Coffee Sales Dashboard", layout="wide")

DATA_PATH = Path(__file__).resolve().parent / "data" / "Afficionado Coffee Roasters.xlsx - Transactions (1).csv"
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["transaction_datetime"] = pd.to_datetime(
        df["year"].astype(str) + " " + df["transaction_time"].astype(str),
        format="%Y %H:%M:%S",
        errors="coerce",
    )
    df["revenue"] = df["transaction_qty"] * df["unit_price"]
    df["hour"] = df["transaction_datetime"].dt.hour
    df["day_of_week"] = df["transaction_datetime"].dt.day_name()
    df["date"] = df["transaction_datetime"].dt.date
    return df


df = load_data()

st.title("☕ Sales Trend and Time-Based Performance Analysis for Afficionado Coffee Roasters")
st.caption("Explore sales performance by location, weekday, hour, and metric choice.")

st.sidebar.header("Filters")
locations = st.sidebar.multiselect(
    "Select Store Location",
    options=sorted(df["store_location"].dropna().unique()),
    default=sorted(df["store_location"].dropna().unique()),
)
days = st.sidebar.multiselect(
    "Select Days of Week",
    options=DAY_ORDER,
    default=DAY_ORDER,
)
hours = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
show_revenue = st.sidebar.toggle("Show Revenue instead of quantity", value=True)

metric_col = "revenue" if show_revenue else "transaction_qty"
metric_label = "Revenue" if show_revenue else "Transaction Quantity"

filtered_df = df[
    df["store_location"].isin(locations)
    & df["day_of_week"].isin(days)
    & df["hour"].between(hours[0], hours[1])
].copy()

if filtered_df.empty:
    st.warning("No data matches the current filters. Please broaden the selection.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Revenue", f"${filtered_df['revenue'].sum():,.0f}")
with col2:
    st.metric("🛒 Transaction Quantity", f"{filtered_df['transaction_qty'].sum():,}")
with col3:
    st.metric("📦 Total Orders", f"{filtered_df['transaction_id'].nunique():,}")

st.subheader("📈 Overall Sales Trend")
daily_sales = filtered_df.resample("D", on="transaction_datetime")[metric_col].sum()
fig_daily = px.line(
    x=daily_sales.index,
    y=daily_sales.values,
    markers=True,
    labels={"x": "Date", "y": metric_label},
    title=f"Daily {metric_label} Trend",
)
fig_daily.update_traces(line_color="#2563eb")
st.plotly_chart(fig_daily, use_container_width=True)

peak_day = daily_sales.idxmax()
low_day = daily_sales.idxmin()
st.info(f"📈 Peak day: **{peak_day.date()}** • 📉 Lowest day: **{low_day.date()}**")

weekly_sales = filtered_df.resample("W", on="transaction_datetime")[metric_col].sum()
fig_weekly = px.line(
    x=weekly_sales.index,
    y=weekly_sales.values,
    markers=True,
    labels={"x": "Week", "y": metric_label},
    title=f"Weekly {metric_label} Trend",
)
st.plotly_chart(fig_weekly, use_container_width=True)

monthly_sales = filtered_df.resample("ME", on="transaction_datetime")[metric_col].sum()
fig_monthly = px.line(
    x=monthly_sales.index,
    y=monthly_sales.values,
    markers=True,
    labels={"x": "Month", "y": metric_label},
    title=f"Monthly {metric_label} Trend",
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.subheader("📊 Day-of-Week Performance")
dow_sales = (
    filtered_df.groupby("day_of_week")[metric_col]
    .sum()
    .reindex(DAY_ORDER)
)
fig_dow = px.bar(
    x=dow_sales.index,
    y=dow_sales.values,
    text=dow_sales.values,
    labels={"x": "Day of Week", "y": metric_label},
    title=f"{metric_label} by Day of Week",
)
fig_dow.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_dow, use_container_width=True)

st.subheader("⏰ Hourly Demand Heatmap")
hourly_sales = (
    filtered_df.pivot_table(index="day_of_week", columns="hour", values=metric_col, aggfunc="sum")
    .reindex(DAY_ORDER)
)
fig_heatmap = px.imshow(
    hourly_sales,
    labels={"x": "Hour of Day", "y": "Day of Week", "color": metric_label},
    title=f"{metric_label} by Hour and Day",
    color_continuous_scale="Viridis",
)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.subheader(f"🏪 {metric_label} by Store Location")
location_sales = filtered_df.groupby("store_location")[metric_col].sum().sort_values(ascending=False)
fig_location = px.bar(
    x=location_sales.index,
    y=location_sales.values,
    text=location_sales.values,
    labels={"x": "Store Location", "y": metric_label},
    title=f"{metric_label} by Store Location",
)
fig_location.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_location, use_container_width=True)