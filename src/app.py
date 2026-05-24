"""
Customer Segmentation & Risk Evaluation - Executive Dashboard

An interactive Streamlit application for exploring customer segments, risk profiles,
and portfolio metrics from a synthetic B2B customer dataset.

This dashboard demonstrates:
- Customer segmentation based on revenue, margin, and payment behavior
- Risk scoring and categorization
- BI-ready export for Power BI and other platforms
- Executive KPIs and segment analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Customer Segmentation & Risk Evaluation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# DATA LOADING
# ============================================================================


@st.cache_data
def load_data():
    """Load processed data from pipeline outputs."""
    data_dir = Path(__file__).resolve().parent.parent / "data"

    # Load main datasets. The pipeline writes segment and risk fields into
    # customer_features.csv so the app can use one stable customer-level table.
    features = pd.read_csv(data_dir / "processed" / "customer_features.csv")
    segment_summary = pd.read_csv(data_dir / "processed" / "segment_summary.csv")
    powerbi = pd.read_csv(data_dir / "powerbi" / "powerbi_customer_dashboard.csv")

    df = features.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    text_cols = [col for col in df.columns if col not in numeric_cols]
    df[numeric_cols] = df[numeric_cols].fillna(0)
    df[text_cols] = df[text_cols].fillna("Unknown")

    return df, segment_summary, powerbi


def format_currency(value):
    """Format value as currency."""
    if pd.isna(value):
        return "€0"
    return f"€{value:,.0f}"


def format_percent(value):
    """Format value as percentage."""
    if pd.isna(value):
        return "0%"
    return f"{value*100:.1f}%"


# ============================================================================
# PAGE: EXECUTIVE OVERVIEW
# ============================================================================


def page_executive_overview(df, segment_summary):
    """Display executive overview with KPIs and high-level metrics."""
    st.title("📊 Executive Overview")
    st.markdown(
        "Comprehensive view of customer portfolio health, risk exposure, and segment distribution."
    )

    # KPI Row 1
    col1, col2, col3, col4, col5 = st.columns(5)

    total_customers = len(df)
    total_revenue = df["annual_revenue"].sum()
    avg_margin = df["gross_margin"].mean()
    high_risk_pct = (df["risk_category"].isin(["Elevated Risk", "High Risk"])).sum() / len(df)
    avg_payment_delay = df["payment_delay_days"].mean()

    with col1:
        st.metric("Total Customers", f"{total_customers:,}")

    with col2:
        st.metric("Total Revenue", format_currency(total_revenue))

    with col3:
        st.metric("Avg Margin", format_percent(avg_margin))

    with col4:
        st.metric("High Risk %", format_percent(high_risk_pct))

    with col5:
        st.metric("Avg Payment Delay", f"{avg_payment_delay:.1f} days")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Segment distribution
        st.subheader("Customer Distribution by Segment")
        segment_counts = df["segment_name"].value_counts()
        fig = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Risk category distribution
        st.subheader("Risk Category Distribution")
        risk_counts = df["risk_category"].value_counts()
        risk_order = ["Low Risk", "Medium Risk", "Elevated Risk", "High Risk"]
        risk_counts = risk_counts.reindex([r for r in risk_order if r in risk_counts.index])
        colors = {"Low Risk": "green", "Medium Risk": "yellow", "Elevated Risk": "orange", "High Risk": "red"}
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map=colors,
            labels={"x": "Risk Category", "y": "Number of Customers"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Segment summary table
    st.subheader("Segment Summary")
    display_cols = [
        "number_of_customers",
        "total_revenue",
        "total_exposure",
        "avg_margin",
        "avg_payment_delay",
        "high_risk_customer_share",
        "recommended_action",
    ]
    summary_display = segment_summary[[col for col in display_cols if col in segment_summary.columns]].copy()

    # Format columns
    if "total_revenue" in summary_display.columns:
        summary_display["total_revenue"] = summary_display["total_revenue"].apply(lambda x: format_currency(x))
    if "total_exposure" in summary_display.columns:
        summary_display["total_exposure"] = summary_display["total_exposure"].apply(lambda x: format_currency(x))
    if "avg_margin" in summary_display.columns:
        summary_display["avg_margin"] = summary_display["avg_margin"].apply(lambda x: format_percent(x))
    if "high_risk_customer_share" in summary_display.columns:
        summary_display["high_risk_customer_share"] = summary_display["high_risk_customer_share"].apply(
            lambda x: format_percent(x)
        )

    st.dataframe(summary_display, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: SEGMENT ANALYSIS
# ============================================================================


def page_segment_analysis(df):
    """Display detailed segment analysis."""
    st.title("🎯 Segment Analysis")
    st.markdown("Deep dive into customer segment characteristics and performance metrics.")

    # Segment selector
    selected_segment = st.selectbox("Select Segment", sorted(df["segment_name"].unique()))

    segment_df = df[df["segment_name"] == selected_segment]

    # Segment details
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Customers", len(segment_df))

    with col2:
        st.metric("Total Revenue", format_currency(segment_df["annual_revenue"].sum()))

    with col3:
        st.metric("Avg Margin", format_percent(segment_df["gross_margin"].mean()))

    with col4:
        st.metric("Avg Risk Score", f"{segment_df['risk_score'].mean():.2f}")

    st.divider()

    # Detailed metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Payment Behavior")
        st.metric("Avg Payment Delay", f"{segment_df['payment_delay_days'].mean():.1f} days")
        st.metric("Overdue Amount", format_currency(segment_df["overdue_amount"].sum()))
        st.metric("Overdue Ratio", format_percent(segment_df["overdue_ratio"].mean()))

    with col2:
        st.subheader("Exposure Metrics")
        st.metric("Total Exposure", format_currency(segment_df["current_exposure"].sum()))
        st.metric("Avg Utilization", format_percent(segment_df["exposure_utilization"].mean()))
        st.metric("Avg Relationship", f"{segment_df['relationship_length_months'].mean():.0f} months")

    with col3:
        st.subheader("Risk Profile")
        risk_dist = segment_df["risk_category"].value_counts()
        st.text(f"Risk Distribution:\n{risk_dist.to_string()}")

    st.divider()

    # Revenue by sub-dimension
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Country (Segment)")
        country_revenue = (
            segment_df.groupby("country")["annual_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig = px.bar(x=country_revenue.index, y=country_revenue.values, labels={"x": "Country", "y": "Revenue"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue by Industry (Segment)")
        industry_revenue = (
            segment_df.groupby("industry")["annual_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig = px.bar(
            x=industry_revenue.index, y=industry_revenue.values, labels={"x": "Industry", "y": "Revenue"}
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: RISK EVALUATION
# ============================================================================


def page_risk_evaluation(df):
    """Display risk analysis and exposure metrics."""
    st.title("⚠️ Risk Evaluation")
    st.markdown("Comprehensive risk assessment and exposure analysis across the portfolio.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Exposure at Risk", format_currency(df["exposure_at_risk"].sum()))

    with col2:
        st.metric("Average Risk Score", f"{df['risk_score'].mean():.2f}")

    with col3:
        st.metric("Customers in High Risk", f"{(df['risk_category'] == 'High Risk').sum()} ({format_percent((df['risk_category'] == 'High Risk').mean())})")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Score Distribution")
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df["risk_score"],
                nbinsx=20,
                name="Risk Score",
                marker_color="#636EFA",
            )
        )
        fig.update_xaxes(title_text="Risk Score")
        fig.update_yaxes(title_text="Number of Customers")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk vs Revenue Scatter")
        fig = px.scatter(
            df,
            x="annual_revenue",
            y="risk_score",
            color="risk_category",
            hover_data=["customer_id", "segment_name"],
            color_discrete_map={
                "Low Risk": "green",
                "Medium Risk": "yellow",
                "Elevated Risk": "orange",
                "High Risk": "red",
            },
        )
        fig.update_xaxes(title_text="Annual Revenue (€)")
        fig.update_yaxes(title_text="Risk Score")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("High-Risk Exposure by Country")
        high_risk = df[df["risk_category"].isin(["Elevated Risk", "High Risk"])]
        country_exposure = (
            high_risk.groupby("country")["exposure_at_risk"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig = px.bar(x=country_exposure.index, y=country_exposure.values, labels={"x": "Country", "y": "Exposure"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Overdue Amount by Country")
        country_overdue = (
            df.groupby("country")["overdue_amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        fig = px.bar(x=country_overdue.index, y=country_overdue.values, labels={"x": "Country", "y": "Overdue Amount"})
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: REVENUE & MARGIN
# ============================================================================


def page_revenue_margin(df):
    """Display revenue and margin analysis."""
    st.title("💰 Revenue & Margin Analysis")
    st.markdown("Portfolio profitability, revenue distribution, and margin analysis.")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Revenue", format_currency(df["annual_revenue"].sum()))

    with col2:
        st.metric("Total Gross Profit", format_currency(df["gross_profit"].sum()))

    with col3:
        st.metric("Avg Margin", format_percent(df["gross_margin"].mean()))

    with col4:
        st.metric("Margin Range", f"{df['gross_margin'].min():.1%} - {df['gross_margin'].max():.1%}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Segment")
        segment_revenue = df.groupby("segment_name")["annual_revenue"].sum().sort_values(ascending=False)
        fig = px.bar(
            x=segment_revenue.index,
            y=segment_revenue.values,
            labels={"x": "Segment", "y": "Revenue (€)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Margin by Segment")
        segment_margin = df.groupby("segment_name")["gross_margin"].mean().sort_values(ascending=False)
        fig = px.bar(
            x=segment_margin.index,
            y=segment_margin.values,
            labels={"x": "Segment", "y": "Avg Margin"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Industry")
        industry_revenue = df.groupby("industry")["annual_revenue"].sum().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=industry_revenue.index,
            y=industry_revenue.values,
            labels={"x": "Industry", "y": "Revenue (€)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Margin by Industry")
        industry_margin = df.groupby("industry")["gross_margin"].mean().sort_values(ascending=False).head(10)
        fig = px.bar(
            x=industry_margin.index,
            y=industry_margin.values,
            labels={"x": "Industry", "y": "Avg Margin"},
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: CUSTOMER DRILLDOWN
# ============================================================================


def page_customer_drilldown(df):
    """Display customer-level details and drilldown."""
    st.title("🔍 Customer Drilldown")
    st.markdown("Explore individual customer profiles and details.")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        segment_filter = st.multiselect("Segment", options=sorted(df["segment_name"].unique()))

    with col2:
        risk_filter = st.multiselect("Risk Category", options=sorted(df["risk_category"].unique()))

    with col3:
        country_filter = st.multiselect("Country", options=sorted(df["country"].unique()))

    with col4:
        industry_filter = st.multiselect("Industry", options=sorted(df["industry"].unique()))

    # Apply filters
    filtered_df = df.copy()

    if segment_filter:
        filtered_df = filtered_df[filtered_df["segment_name"].isin(segment_filter)]

    if risk_filter:
        filtered_df = filtered_df[filtered_df["risk_category"].isin(risk_filter)]

    if country_filter:
        filtered_df = filtered_df[filtered_df["country"].isin(country_filter)]

    if industry_filter:
        filtered_df = filtered_df[filtered_df["industry"].isin(industry_filter)]

    st.markdown(f"**Showing {len(filtered_df)} customers**")

    # Display table
    display_cols = [
        "customer_id",
        "country",
        "industry",
        "annual_revenue",
        "gross_margin",
        "segment_name",
        "risk_score",
        "risk_category",
        "payment_delay_days",
        "overdue_amount",
        "current_exposure",
    ]

    table_df = filtered_df[[col for col in display_cols if col in filtered_df.columns]].copy()

    # Format columns
    if "annual_revenue" in table_df.columns:
        table_df["annual_revenue"] = table_df["annual_revenue"].apply(lambda x: f"€{x:,.0f}")

    if "gross_margin" in table_df.columns:
        table_df["gross_margin"] = table_df["gross_margin"].apply(lambda x: f"{x:.1%}")

    if "overdue_amount" in table_df.columns:
        table_df["overdue_amount"] = table_df["overdue_amount"].apply(lambda x: f"€{x:,.0f}")

    if "current_exposure" in table_df.columns:
        table_df["current_exposure"] = table_df["current_exposure"].apply(lambda x: f"€{x:,.0f}")

    st.dataframe(table_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: METHODOLOGY & DATA QUALITY
# ============================================================================


def page_methodology():
    """Display methodology and data quality information."""
    st.title("📋 Methodology & Data Quality")

    st.markdown(
        """
### Project Overview

This dashboard presents a **synthetic B2B customer portfolio analysis** designed for portfolio demonstration purposes.

**Data Source:** Fully synthetic customer data generated deterministically (RANDOM_SEED=42) to ensure reproducibility.

### Methodology

#### 1. Data Generation
- 120 synthetic B2B customers across 7 countries and 7 industries
- Realistic distributions for revenue, margin, payment behavior, and credit exposure
- All data is synthetic and does not represent real companies or actual financial information

#### 2. Feature Engineering
Engineered features include:
- **Payment Metrics:** Payment delay days, overdue ratio, payment delay category
- **Profitability:** Revenue per order, gross profit, annual gross profit
- **Credit Exposure:** Exposure utilization %, exposure at risk
- **Customer Health:** Relationship tenure, order frequency
- **Risk Indicators:** Payment behavior patterns, concentration risk

#### 3. Segmentation (KMeans Clustering)
Customers are segmented into 5 groups based on:
- Annual revenue
- Overdue ratio
- Payment delay
- Gross margin
- Exposure utilization

Segments are business-labeled for interpretation:
- **Strategic High-Value:** High revenue, excellent payment history
- **Stable Low-Risk:** Consistent, predictable, low default risk
- **Growth Potential:** Above-average revenue with moderate risk
- **Late-Paying Watchlist:** Acceptable revenue but payment concerns
- **High-Risk Low-Margin:** Limited profitability with elevated risk

#### 4. Risk Scoring
Composite risk score combining:
- Overdue ratio (8x weight)
- Payment delay (0.033x weight per day)
- Margin quality (4x weight)
- Default flag (15x weight if present)
- Exposure utilization (2x weight)
- Relationship tenure (-0.1x weight)

**Risk Categories:**
- **Low Risk (0-2.5):** Strong payment, low utilization, healthy margin
- **Medium Risk (2.5-5.0):** Acceptable payment behavior, normal utilization
- **Elevated Risk (5.0-8.0):** Notable delays, higher utilization, margin concerns
- **High Risk (8.0+):** Serious payment issues, high utilization, low margin

### Important Disclaimer

⚠️ **This analysis uses fully synthetic data created for portfolio demonstration purposes.**

- No real company or customer data is included
- Risk scores are illustrative only
- **Not suitable for actual credit decisions**
- Designed to demonstrate analytical capabilities, not real business impact
- For production use, engage regulatory and credit risk specialists

### Output Datasets

1. **customer_features.csv:** Engineered customer-level attributes
2. **customer_segments.csv:** Cluster-based segment assignments
3. **risk_scored_customers.csv:** Risk scores and categories
4. **segment_summary.csv:** Aggregated segment metrics
5. **powerbi_customer_dashboard.csv:** BI-ready export

### Technical Stack

- **Python:** pandas, numpy, scikit-learn, streamlit
- **Data Processing:** Feature engineering, KMeans clustering
- **Visualization:** Plotly, Streamlit
- **Reproducibility:** Deterministic random seed, version control
        """
    )

    st.info(
        "This dashboard is part of a portfolio project demonstrating data analytics, Python development, "
        "and business intelligence capabilities. All data is synthetic."
    )


# ============================================================================
# MAIN APP
# ============================================================================


def main():
    """Main Streamlit app."""
    # Load data
    df, segment_summary, powerbi = load_data()

    # Sidebar navigation
    st.sidebar.title("Customer Segmentation Dashboard")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Select Page",
        [
            "Executive Overview",
            "Segment Analysis",
            "Risk Evaluation",
            "Revenue & Margin",
            "Customer Drilldown",
            "Methodology",
        ],
    )

    # Page routing
    if page == "Executive Overview":
        page_executive_overview(df, segment_summary)

    elif page == "Segment Analysis":
        page_segment_analysis(df)

    elif page == "Risk Evaluation":
        page_risk_evaluation(df)

    elif page == "Revenue & Margin":
        page_revenue_margin(df)

    elif page == "Customer Drilldown":
        page_customer_drilldown(df)

    else:  # Methodology
        page_methodology()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Synthetic Portfolio Dashboard**\n\n"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "Data: 100% synthetic, portfolio demonstration"
    )


if __name__ == "__main__":
    main()
