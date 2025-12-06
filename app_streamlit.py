# app_streamlit.py
import streamlit as st
import pandas as pd
import plotly.express as px

# --------- PAGE CONFIG ---------
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="🛒",
    layout="wide",
)

# --------- LOAD DATA ---------
@st.cache_data
def load_data():
    # Prefer labeled file if available
    try:
        df = pd.read_csv("rfm_with_clusters_labeled.csv")
    except FileNotFoundError:
        df = pd.read_csv("rfm_with_clusters.csv")
        # fall back to generic segment names
        df["Segment"] = "Cluster " + df["KM_Cluster"].astype(str)
    return df

rfm = load_data()

if "Segment" not in rfm.columns:
    rfm["Segment"] = "Cluster " + rfm["KM_Cluster"].astype(str)

# --------- SIDEBAR ---------
st.sidebar.title("⚙️ Controls")

segments = sorted(rfm["Segment"].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Select Segments",
    options=segments,
    default=segments,
)

monetary_min = float(rfm["Monetary"].min())
monetary_max = float(rfm["Monetary"].max())

monetary_range = st.sidebar.slider(
    "Filter by Monetary (Total Spend)",
    min_value=monetary_min,
    max_value=monetary_max,
    value=(monetary_min, monetary_max),
    step=100.0,
)

show_raw = st.sidebar.checkbox("Show raw RFM data", value=False)

# Apply filters
filtered = rfm[
    (rfm["Segment"].isin(selected_segments)) &
    (rfm["Monetary"].between(monetary_range[0], monetary_range[1]))
].copy()

# --------- HEADER ---------
st.markdown(
    """
    <h1 style="margin-bottom:0px;">Customer Segmentation Dashboard</h1>
    <p style="color:gray; margin-top:0px;">
        RFM-based clustering of customers to identify key segments and drive marketing strategies.
    </p>
    """,
    unsafe_allow_html=True,
)

# --------- TOP KPI CARDS ---------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Customers (Filtered)",
        f"{filtered['CustomerID'].nunique():,}"
    )

with col2:
    st.metric(
        "Total Revenue (Filtered)",
        f"{filtered['Monetary'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Avg Monetary per Customer",
        f"{filtered['Monetary'].mean():,.0f}"
    )

with col4:
    st.metric(
        "Number of Segments",
        f"{filtered['Segment'].nunique()}"
    )

st.markdown("---")

# --------- TABS LAYOUT ---------
tab_overview, tab_clusters = st.tabs(["📊 Overview", "🔍 Cluster Details"])

# ======= OVERVIEW TAB =======
with tab_overview:
    st.subheader("Segment Summary")

    summary = (
        filtered.groupby(["KM_Cluster", "Segment"])
        .agg(
            Monetary=("Monetary", "mean"),
            Frequency=("Frequency", "mean"),
            Recency=("Recency", "mean"),
            NumCustomers=("CustomerID", "nunique"),
            TotalRevenue=("Monetary", "sum"),
        )
        .reset_index()
        .sort_values("TotalRevenue", ascending=False)
    )

    st.dataframe(
        summary.style.format({
            "Monetary": "{:,.0f}",
            "Frequency": "{:,.1f}",
            "Recency": "{:,.1f}",
            "NumCustomers": "{:,.0f}",
            "TotalRevenue": "{:,.0f}",
        }),
        use_container_width=True,
        height=280,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Revenue by Segment")
        fig_rev = px.bar(
            summary,
            x="Segment",
            y="TotalRevenue",
            color="Segment",
            text="TotalRevenue",
        )
        fig_rev.update_layout(
            xaxis_title="Segment",
            yaxis_title="Total Revenue",
            showlegend=False,
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with c2:
        st.markdown("#### Customer Count by Segment")
        fig_cnt = px.bar(
            summary,
            x="Segment",
            y="NumCustomers",
            color="Segment",
            text="NumCustomers",
        )
        fig_cnt.update_layout(
            xaxis_title="Segment",
            yaxis_title="Number of Customers",
            showlegend=False,
        )
        st.plotly_chart(fig_cnt, use_container_width=True)

    st.markdown("#### Monetary vs Frequency (Colored by Segment)")
    fig_scatter = px.scatter(
        filtered,
        x="Frequency",
        y="Monetary",
        color="Segment",
        hover_data=["CustomerID", "Recency", "KM_Cluster"],
    )
    fig_scatter.update_layout(
        xaxis_title="Frequency",
        yaxis_title="Monetary",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ======= CLUSTER DETAILS TAB =======
with tab_clusters:
    st.subheader("Cluster-Level RFM Distribution")

    cluster_to_focus = st.selectbox(
        "Select Segment for Detailed View",
        options=segments,
        index=0
    )

    detail_df = filtered[filtered["Segment"] == cluster_to_focus]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(
            f"{cluster_to_focus} – Customers",
            f"{detail_df['CustomerID'].nunique():,}"
        )
    with c2:
        st.metric(
            f"{cluster_to_focus} – Avg Monetary",
            f"{detail_df['Monetary'].mean():,.0f}"
        )
    with c3:
        st.metric(
            f"{cluster_to_focus} – Avg Recency (days)",
            f"{detail_df['Recency'].mean():.1f}"
        )

    c4, c5 = st.columns(2)
    with c4:
        st.markdown("##### Recency Distribution")
        fig_rec = px.histogram(
            detail_df,
            x="Recency",
            nbins=30,
        )
        fig_rec.update_layout(xaxis_title="Recency (days)")
        st.plotly_chart(fig_rec, use_container_width=True)

    with c5:
        st.markdown("##### Monetary Distribution")
        fig_mon = px.histogram(
            detail_df,
            x="Monetary",
            nbins=30,
        )
        fig_mon.update_layout(xaxis_title="Monetary value")
        st.plotly_chart(fig_mon, use_container_width=True)

# --------- RAW DATA (OPTIONAL) ---------
if show_raw:
    st.markdown("### Raw RFM + Clusters Data (Filtered)")
    st.dataframe(filtered, use_container_width=True, height=400)
