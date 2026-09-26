import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(
    page_title="Fire Detector — Maharashtra",
    page_icon="🔥",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .header-banner {
        background: linear-gradient(135deg, #1c1f26 0%, #14161a 100%);
        border: 1px solid #2d3139;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        font-size: 60px !important;
        font-weight: 800 !important;
        color: #f0f2f6;
        margin: 0;
    }
    .header-subtitle {
        color: #9ca3af;
        font-size: 14px;
        margin-top: 4px;
    }
    .live-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background-color: #1a2e1a;
        border: 1px solid #2d5a2d;
        color: #4ade80;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #4ade80;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.6); }
        70% { box-shadow: 0 0 0 8px rgba(74, 222, 128, 0); }
        100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
    }

    .metric-card {
        background: linear-gradient(145deg, #1c1f26, #14161a);
        padding: 22px 20px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid #2d3139;
    }
    .metric-number { font-size: 34px; font-weight: 800; color: #ff6b4a; }
    .metric-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    .alert-card {
        background-color: #241414;
        border-left: 4px solid #ff4b4b;
        border-radius: 6px;
        padding: 8px 14px;
        margin-bottom: 6px;
    }
    .alert-title { font-weight: 700; color: #ff6b6b; font-size: 14px; }
    .alert-detail { color: #d1d5db; font-size: 13px; margin-top: 2px; }
    .alert-location { color: #9ca3af; font-size: 12px; margin-top: 2px; }

    .map-container {
        border: 1px solid #2d3139;
        border-radius: 12px;
        overflow: hidden;
    }

    .legend-box {
        background-color: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 12px;
        display: flex;
        gap: 24px;
        flex-wrap: wrap;
        font-size: 13px;
        color: #d1d5db;
    }
    
    .section-card {
        background-color: #14161a;
        border: 1px solid #2d3139;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 24px;
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #f0f2f6;
        margin-bottom: 4px;
    }
    .section-subtitle {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 12px;
    }

    section[data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #2d3139; }
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("""
<div class="header-banner">
    <div>
        <p class="header-title">🔥 Active Fire Detection</p>
        <p class="header-subtitle">Maharashtra — Near real-time thermal anomaly detection using NASA FIRMS VIIRS data</p>
    </div>
    <div class="live-badge"><div class="pulse-dot"></div> LIVE</div>
</div>
""", unsafe_allow_html=True)

df = pd.read_csv("data/fires_classified.csv")

st.sidebar.markdown("### Filters")
min_frp = st.sidebar.slider("Minimum Fire Radiative Power (FRP)", 0.0, float(df["frp"].max()), 0.0)
selected_daynight = st.sidebar.multiselect("Detection time", options=df["daynight"].unique(), default=list(df["daynight"].unique()))

filtered_df = df[(df["frp"] >= min_frp) & (df["daynight"].isin(selected_daynight))]

# ---- Metric cards ----
col1, col2, col3, col4 = st.columns(4)
metrics = [
    (len(filtered_df), "Total Detections"),
    (f'{filtered_df["frp"].mean():.1f}', "Avg FRP"),
    (f'{filtered_df["frp"].max():.1f}', "Max FRP"),
    (len(filtered_df[filtered_df["fire_type"] == "Industrial"]), "Industrial Fires"),
]
for col, (value, label) in zip([col1, col2, col3, col4], metrics):
    col.markdown(f'<div class="metric-card"><div class="metric-number">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

st.write("")

def get_color(frp):
    if frp < 5:
        return "#ffd93d"
    elif frp < 15:
        return "#ff8c42"
    else:
        return "#c1121f"

# ---- Two-column layout: Map on left, Alerts + Pie chart stacked on right ----
map_col, side_col = st.columns([2.5, 1])

with map_col:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    m = folium.Map(location=[19.5, 76.0], zoom_start=6, tiles="OpenStreetMap")
    for _, row in filtered_df.iterrows():
        is_industrial = row["fire_type"] == "Industrial"
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8 if is_industrial else 6,
            color="#4FD1C5" if is_industrial else get_color(row["frp"]),
            fill=True,
            fill_color=get_color(row["frp"]),
            fill_opacity=0.85,
            weight=3 if is_industrial else 1,
            popup=folium.Popup(
                (f"Type: {row['fire_type']} | FRP: {row['frp']} | Confidence: {row['predicted_probability_industrial']*100:.0f}% | Date: {row['acq_date']}"
                 if row['fire_type'] == 'Industrial' else
                 f"Type: {row['fire_type']} | FRP: {row['frp']} | Confidence: {(1-row['predicted_probability_industrial'])*100:.0f}% | Date: {row['acq_date']}"),
                max_width=220
            )
        ).add_to(m)

    try:
        persistent_df = pd.read_csv("data/persistent_sources.csv")
        persistent_df = persistent_df[persistent_df["is_persistent"] == True]
        for _, prow in persistent_df.iterrows():
            folium.CircleMarker(
                location=[prow["latitude"], prow["longitude"]],
                radius=14,
                color="#1e3a8a",
                weight=3,
                fill=False,
                popup=folium.Popup(
                    f"<b>Persistent Thermal Source</b><br>"
                    f"Detected on {prow['days_detected']} separate days<br>"
                    f"Location: {prow['latitude']:.4f}, {prow['longitude']:.4f}<br>"
                    f"Risk level: {'High' if prow['days_detected'] >= 30 else 'Moderate'}",
                    max_width=220
                )
            ).add_to(m)
    except FileNotFoundError:
        pass

    st_folium(m, width=None, height=560)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="legend-box">
        <div>🟡 Low FRP (&lt;5)</div>
        <div>🟠 Medium FRP (5–15)</div>
        <div>🔴 High FRP (&gt;15)</div>
        <div>🔵 Teal border = Classified Industrial</div>
        <div>⭕ Dark blue ring = Persistent Source</div>
    </div>
    """, unsafe_allow_html=True)

with side_col:
    # ---- Alerts, stacked at top of right column ----
    alerts = filtered_df[filtered_df["fire_type"] == "Industrial"].sort_values("frp", ascending=False).head(3)

    if len(alerts) > 0:
        st.markdown(f"##### 🚨 {len(alerts)} High-Priority Alert(s)")
        for _, arow in alerts.iterrows():
            conf = arow["predicted_probability_industrial"] * 100
            st.markdown(f"""
            <div class="alert-card">
                <div class="alert-title">⚠️ Industrial Fire</div>
                <div class="alert-detail">FRP: {arow['frp']:.1f} | Conf: {conf:.0f}%</div>
                <div class="alert-location">📍 {arow['latitude']:.4f}, {arow['longitude']:.4f}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("✅ No active alerts.")

    st.write("")

    # ---- Pie chart, below alerts in the same column ----
    st.markdown("##### Fire Type Breakdown")
    type_counts = filtered_df["fire_type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig = px.pie(
        type_counts, names="Type", values="Count",
        color="Type",
        color_discrete_map={"Industrial": "#4FD1C5", "Other (Vegetation/Agricultural)": "#ff8c42"},
        hole=0.5
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#d1d5db",
        margin=dict(l=10, r=10, t=10, b=10),
        height=280,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3)
    )
    st.plotly_chart(fig, use_container_width=True)
# ---- Historical trend, full-width section below map+sidebar row ----
with st.container(border=True):
    st.markdown('<div class="section-title">📈 Historical Fire Activity — Last 6 Months</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Monthly detection counts reveal seasonal burning patterns across Maharashtra</div>', unsafe_allow_html=True)

    try:
        hist_df = pd.read_csv("data/fires_historical.csv")
        hist_df["acq_date"] = pd.to_datetime(hist_df["acq_date"])
        hist_df["month"] = hist_df["acq_date"].dt.strftime("%b %Y")
        monthly = hist_df.groupby("month").size().reset_index(name="count")

        month_order = hist_df.drop_duplicates("month").sort_values("acq_date")["month"].tolist()
        monthly["month"] = pd.Categorical(monthly["month"], categories=month_order, ordered=True)
        monthly = monthly.sort_values("month")

        fig_hist = px.bar(
            monthly, x="month", y="count",
            color_discrete_sequence=["#ff6b4a"]
        )
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#d1d5db",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            xaxis_title=None,
            yaxis_title="Detections"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    except FileNotFoundError:
        st.markdown("Historical data not available.")