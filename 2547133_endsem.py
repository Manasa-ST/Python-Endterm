import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="GATEWAY TECHFEST-2025 Analytics",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("fest_dataset.csv")
    df.columns = df.columns.str.strip()
    return df

df_full = load_data()

# -----------------------------
# STATE NAME FIX (IMPORTANT)
# -----------------------------
STATE_MAPPING = {
    "TN": "Tamil Nadu",
    "KA": "Karnataka",
    "KL": "Kerala",
    "AP": "Andhra Pradesh",
    "TS": "Telangana",
    "MH": "Maharashtra",
    "GJ": "Gujarat",
    "RJ": "Rajasthan",
    "UP": "Uttar Pradesh",
    "WB": "West Bengal",
    "MP": "Madhya Pradesh",
    "DL": "Delhi",
    "HR": "Haryana",
    "PB": "Punjab",
    "BR": "Bihar",
    "OR": "Odisha",
    "AS": "Assam"
}

df_full["State"] = df_full["State"].replace(STATE_MAPPING)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard Overview",
        "Participation Analysis",
        "Geographic Insights",
        "Feedback and Ratings",
        "Data Export"
    ]
)

st.sidebar.markdown("---")

# -----------------------------
# FILTERS
# -----------------------------
events = ["All Events"] + sorted(df_full["Event Name"].unique())
colleges = ["All Colleges"] + sorted(df_full["College"].unique())
states = ["All States"] + sorted(df_full["State"].unique())

selected_event = st.sidebar.selectbox("Select Event", events)
selected_college = st.sidebar.selectbox("Select College", colleges)
selected_state = st.sidebar.selectbox("Select State", states)

min_rating = int(df_full["Rating"].min())
max_rating = int(df_full["Rating"].max())

rating_range = st.sidebar.slider(
    "Select Rating Range",
    min_value=min_rating,
    max_value=max_rating,
    value=(min_rating, max_rating)
)

# -----------------------------
# APPLY FILTERS
# -----------------------------
df = df_full.copy()

if selected_event != "All Events":
    df = df[df["Event Name"] == selected_event]

if selected_college != "All Colleges":
    df = df[df["College"] == selected_college]

if selected_state != "All States":
    df = df[df["State"] == selected_state]

df = df[
    (df["Rating"] >= rating_range[0]) &
    (df["Rating"] <= rating_range[1])
]

# -----------------------------
# PAGE 1 — DASHBOARD OVERVIEW
# -----------------------------
if page == "Dashboard Overview":

    st.title("GATEWAYS TECHFEST-2025 Analytics and Insights Portal")

    total_participants = len(df)
    total_events = df["Event Name"].nunique()
    total_colleges = df["College"].nunique()
    avg_rating = round(df["Rating"].mean(), 2)

    st.subheader("Key Metrics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Participants", total_participants)
    c2.metric("Number of Events", total_events)
    c3.metric("Participating Colleges", total_colleges)
    c4.metric("Average Rating", avg_rating)

    st.divider()

    st.subheader("Dataset Preview")
    st.dataframe(df, use_container_width=True)

# -----------------------------
# PAGE 2 — PARTICIPATION ANALYSIS
# -----------------------------
elif page == "Participation Analysis":

    st.title("Participation Analysis")

    col1, col2 = st.columns(2)

    with col1:

        event_counts = (
            df["Event Name"]
            .value_counts()
            .reset_index()
        )

        event_counts.columns = ["Event", "Participants"]

        fig_event = px.bar(
            event_counts,
            x="Participants",
            y="Event",
            orientation="h",
            title="Participants by Event",
            color="Participants",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig_event, use_container_width=True)

    with col2:

        college_counts = (
            df["College"]
            .value_counts()
            .reset_index()
        )

        college_counts.columns = ["College", "Participants"]

        fig_college = px.bar(
            college_counts,
            x="College",
            y="Participants",
            title="Participants by College",
            color="Participants",
            color_continuous_scale="Greens"
        )

        st.plotly_chart(fig_college, use_container_width=True)

    st.divider()

    if "Gender" in df.columns:

        gender_counts = (
            df["Gender"]
            .value_counts()
            .reset_index()
        )

        gender_counts.columns = ["Gender", "Count"]

        fig_gender = px.pie(
            gender_counts,
            names="Gender",
            values="Count",
            hole=0.4,
            title="Gender Distribution"
        )

        st.plotly_chart(fig_gender, use_container_width=True)

# -----------------------------
# PAGE 3 — GEOGRAPHIC INSIGHTS
# -----------------------------
elif page == "Geographic Insights":

    st.title("Geographic Insights")

    st.subheader("State-wise Participation Across India")

    geojson_url = (
        "https://gist.githubusercontent.com/jbrobst/"
        "56c13bbbf9d97d187fea01ca62ea5112/raw/"
        "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    )

    india_states = requests.get(geojson_url).json()

    state_counts = (
        df["State"]
        .value_counts()
        .reset_index()
    )

    state_counts.columns = ["State", "Participants"]

    fig_map = px.choropleth(
        state_counts,
        geojson=india_states,
        featureidkey="properties.ST_NM",
        locations="State",
        color="Participants",
        hover_name="State",
        color_continuous_scale="Blues",
        title="State-wise Participation Across India"
    )

    fig_map.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig_map.update_layout(
        height=550,
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.dataframe(state_counts)

# -----------------------------
# PAGE 4 — FEEDBACK AND RATINGS
# -----------------------------
elif page == "Feedback and Ratings":

    st.title("Feedback and Ratings")

    rating_counts = (
        df["Rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    rating_counts.columns = ["Rating", "Count"]

    fig_rating = px.bar(
        rating_counts,
        x="Rating",
        y="Count",
        title="Ratings Distribution",
        color="Count"
    )

    st.plotly_chart(fig_rating, use_container_width=True)

    st.divider()

    st.subheader("Feedback WordCloud")

    text = " ".join(
        df["Feedback on Fest"]
        .dropna()
        .astype(str)
    )

    if text:

        wc = WordCloud(
            width=800,
            height=400,
            background_color="white"
        ).generate(text)

        fig, ax = plt.subplots()

        ax.imshow(wc)
        ax.axis("off")

        st.pyplot(fig)

    else:

        st.info("No feedback available.")

# -----------------------------
# PAGE 5 — EXPORT
# -----------------------------
elif page == "Data Export":

    st.title("Export Filtered Data")

    csv = df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.markdown(
    "<center><b>TECHFEST-2025 Analytics Dashboard</b></center>",
    unsafe_allow_html=True
)
