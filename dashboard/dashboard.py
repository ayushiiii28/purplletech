# =====================================================
# PURPLLE STORE INTELLIGENCE DASHBOARD
# =====================================================

import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title="Purplle Store Intelligence",

    page_icon="🛍️",

    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""

<style>

/* =====================================================
GLOBAL
===================================================== */

html, body, [class*="css"] {

    font-family:
    Inter,
    system-ui,
    sans-serif;
}

/* =====================================================
BACKGROUND
===================================================== */

.stApp {

    background:
    linear-gradient(
        180deg,
        #07111F 0%,
        #0B1730 45%,
        #101827 100%
    );

    color: #F9FAFB;
}

/* =====================================================
HEADINGS
===================================================== */

h1 {

    color: white !important;

    font-size: 38px !important;

    font-weight: 700 !important;

    letter-spacing: -1px;
}

h2, h3 {

    color: #F3F4F6 !important;

    font-weight: 600 !important;
}

/* =====================================================
CONTAINER SPACING
===================================================== */

.block-container {

    padding-top: 2rem;

    padding-bottom: 2rem;

    max-width: 1500px;
}

/* =====================================================
METRIC CARDS
===================================================== */

.metric-card {

    background:
    rgba(17, 24, 39, 0.88);

    border:
    1px solid rgba(255,255,255,0.06);

    border-radius: 18px;

    padding: 20px 18px;

    min-height: 130px;

    display: flex;

    flex-direction: column;

    justify-content: center;

    transition: 0.2s ease;
}

.metric-card:hover {

    border:
    1px solid rgba(255,255,255,0.12);

    transform: translateY(-2px);
}

/* =====================================================
METRIC LABEL
===================================================== */

.metric-title {

    color: #9CA3AF;

    font-size: 13px;

    font-weight: 500;

    margin-bottom: 12px;

    text-transform: uppercase;

    letter-spacing: 0.5px;
}

/* =====================================================
METRIC VALUE
===================================================== */

.metric-value {

    color: white;

    font-size: 34px;

    font-weight: 700;

    line-height: 1.1;
}

/* =====================================================
SIDEBAR
===================================================== */

[data-testid="stSidebar"] {

    background:
    #08111F;

    border-right:
    1px solid rgba(255,255,255,0.06);
}

/* =====================================================
SIDEBAR TEXT
===================================================== */

[data-testid="stSidebar"] * {

    color: #F3F4F6 !important;
}

/* =====================================================
DATAFRAME
===================================================== */

[data-testid="stDataFrame"] {

    border-radius: 14px;

    overflow: hidden;

    border:
    1px solid rgba(255,255,255,0.06);
            
}
/* =====================================================
STREAMLIT METRIC CARDS
===================================================== */

[data-testid="metric-container"] {

    background:
    rgba(17, 24, 39, 0.88);

    border:
    1px solid rgba(255,255,255,0.06);

    padding: 18px;

    border-radius: 18px;

    box-shadow:
    0 4px 12px rgba(0,0,0,0.18);
}

/* =====================================================
METRIC LABEL
===================================================== */

[data-testid="metric-container"] label {

    color: #9CA3AF !important;

    font-size: 14px !important;
}

/* =====================================================
METRIC VALUE
===================================================== */

[data-testid="metric-container"] [data-testid="stMetricValue"] {

    color: white !important;

    font-size: 34px !important;

    font-weight: 700 !important;
}

</style>

""", unsafe_allow_html=True)

# =====================================================
# TITLE
# =====================================================

st.title("Purplle Store Intelligence")

st.caption(
    "Real-time retail analytics platform for customer movement, queue intelligence, and purchase behavior."
)

# =====================================================
# BACKEND URL
# =====================================================

API_URL = "https://purplletech-1.onrender.com"

# =====================================================
# FETCH DATA
# =====================================================

metrics = requests.get(
    f"{API_URL}/metrics"
).json()

heatmap = requests.get(
    f"{API_URL}/heatmap"
).json()

anomalies = requests.get(
    f"{API_URL}/anomalies"
).json()

events_response = requests.get(
    f"{API_URL}/events"
).json()

events = events_response["events"]

df = pd.DataFrame(events)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("System Overview")

st.sidebar.success(
    "Backend Connected"
)

st.sidebar.markdown("---")

st.sidebar.markdown("""

### Active Components

- Multi-store Analytics
- Queue Intelligence
- Purchase Correlation
- Event Streaming
- FastAPI Backend
- SQLite Persistence
- CV Tracking Pipeline

""")

st.sidebar.markdown("---")

st.sidebar.info(

    f"Top Active Zone: "
    f"{metrics['top_active_zone']}"
)

# =====================================================
# KPI SECTION
# =====================================================

# =====================================================
# KPI SECTION
# =====================================================

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(

        label="Total Events",

        value=metrics["total_events"]
    )

with col2:

    st.metric(

        label="Purchases",

        value=metrics["purchase_events"]
    )

with col3:

    st.metric(

        label="Revenue",

        value=f"₹{metrics['total_revenue_inr']}"
    )

with col4:

    st.metric(

        label="Queue Joins",

        value=metrics["queue_join_events"]
    )

with col5:

    st.metric(

        label="Conversion Rate",

        value=f"{metrics['conversion_rate']}%"
    )

# =====================================================
# CHART STYLE
# =====================================================

chart_layout = dict(

    template="plotly_dark",

    paper_bgcolor="rgba(0,0,0,0)",

    plot_bgcolor="rgba(0,0,0,0)",

    font=dict(

        family="Inter",

        color="white"
    ),

    margin=dict(
        l=20,
        r=20,
        t=40,
        b=20
    )
)

# =====================================================
# EXECUTIVE ANALYTICS
# =====================================================

st.markdown("---")

left, right = st.columns(2)

# =====================================================
# STORE DISTRIBUTION
# =====================================================

with left:

    st.subheader("Store Distribution")

    store_df = pd.DataFrame({

        "Store":
        list(
            metrics["store_distribution"].keys()
        ),

        "Events":
        list(
            metrics["store_distribution"].values()
        )
    })

    fig_store = px.pie(

        store_df,

        names="Store",

        values="Events",

        hole=0.55
    )

    fig_store.update_layout(**chart_layout)

    st.plotly_chart(
        fig_store,
        width="stretch"
    )

# =====================================================
# EVENT DISTRIBUTION
# =====================================================

with right:

    st.subheader("Event Distribution")

    event_counts = (

        df["event_type"]

        .value_counts()

        .reset_index()
    )

    event_counts.columns = [

        "Event Type",

        "Count"
    ]

    fig_events = px.bar(

        event_counts,

        x="Event Type",

        y="Count",

        color="Count"
    )

    fig_events.update_layout(**chart_layout)

    st.plotly_chart(
        fig_events,
        width="stretch"
    )

# =====================================================
# CAMERA + ZONE ANALYTICS
# =====================================================

st.markdown("---")

left2, right2 = st.columns(2)

with left2:

    st.subheader("Camera Analytics")

    camera_df = pd.DataFrame({

        "Camera":
        list(
            metrics["camera_distribution"].keys()
        ),

        "Events":
        list(
            metrics["camera_distribution"].values()
        )
    })

    fig_camera = px.bar(

        camera_df,

        x="Camera",

        y="Events",

        color="Events"
    )

    fig_camera.update_layout(**chart_layout)

    st.plotly_chart(
        fig_camera,
        width="stretch"
    )

with right2:

    st.subheader("Zone Activity")

    heatmap_df = pd.DataFrame({

        "Zone":
        list(
            heatmap["zone_activity"].keys()
        ),

        "Activity":
        list(
            heatmap["zone_activity"].values()
        )
    })

    fig_heatmap = px.bar(

        heatmap_df,

        x="Zone",

        y="Activity",

        color="Activity"
    )

    fig_heatmap.update_layout(**chart_layout)

    st.plotly_chart(
        fig_heatmap,
        width="stretch"
    )

# =====================================================
# CUSTOMER FUNNEL
# =====================================================

st.markdown("---")

st.subheader("Customer Funnel")

funnel_labels = [

    "ENTRY",

    "ZONE_ENTER",

    "QUEUE_JOIN",

    "PURCHASE"
]

funnel_values = [

    metrics["entry_events"],

    metrics["zone_enter_events"],

    metrics["queue_join_events"],

    metrics["purchase_events"]
]

fig_funnel = go.Figure(

    go.Funnel(

        orientation="h",

        y=funnel_labels,

        x=funnel_values
    )
)

fig_funnel.update_layout(**chart_layout)

st.plotly_chart(
    fig_funnel,
    width="stretch"
)

# =====================================================
# ANOMALIES
# =====================================================

st.markdown("---")

st.subheader("Anomaly Detection")

if anomalies["anomalies"]:

    for anomaly in anomalies["anomalies"]:

        st.error(anomaly)

else:

    st.success(
        "No anomalies detected"
    )

# =====================================================
# LIVE EVENT STREAM
# =====================================================

st.markdown("---")

st.subheader("Live Event Stream")

st.dataframe(

    df.tail(25),

    width="stretch"
)

