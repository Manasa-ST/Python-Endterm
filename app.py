import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(layout="wide")

# -----------------------
# Load Data
# -----------------------
df = pd.read_csv("fest_dataset.csv")

st.title("GATEWAYS-2025 Fest Analysis Dashboard")

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("Filter Participants")

states = st.sidebar.multiselect("Select State", df['State'].unique(), default=df['State'].unique())
events = st.sidebar.multiselect("Select Event", df['Event Name'].unique(), default=df['Event Name'].unique())

df = df[(df['State'].isin(states)) & (df['Event Name'].isin(events))]

# -----------------------
# Tabs (IMPORTANT)
# -----------------------
tab1, tab2, tab3 = st.tabs([
    "Participation",
    "Feedback",
    "Dashboard"
])

# =========================
# TAB 1: Participation
# =========================
with tab1:
    st.header("Participation Analysis")

    # Event-wise
    fig1 = px.bar(df['Event Name'].value_counts(),
                  title="Event-wise Participation")
    st.plotly_chart(fig1, use_container_width=True)

    # College-wise
    fig2 = px.bar(df['College'].value_counts().head(10),
                  title="College-wise Participation")
    st.plotly_chart(fig2, use_container_width=True)

    # Event Type
    fig3 = px.pie(df, names='Event Type',
                  title="Event Type Distribution")
    st.plotly_chart(fig3, use_container_width=True)

    # India Map
    st.subheader("State-wise Participation (India Map)")

    state_counts = df['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']

    india_geojson = "https://raw.githubusercontent.com/plotly/datasets/master/india_states.geojson"

    fig_map = px.choropleth(
        state_counts,
        geojson=india_geojson,
        featureidkey="properties.ST_NM",
        locations="State",
        color="Count",
        title="India State-wise Participation",
        color_continuous_scale="Blues"
    )

    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)

# =========================
# TAB 2: Feedback
# =========================
with tab2:
    st.header("Feedback Analysis")

    # Rating Distribution
    fig4 = px.histogram(df, x='Rating', title="Rating Distribution")
    st.plotly_chart(fig4, use_container_width=True)

    # WordCloud
    st.subheader("WordCloud")

    text = " ".join(df['Feedback on Fest'].dropna().astype(str))
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)

    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

# =========================
# TAB 3: Dashboard
# =========================
with tab3:
    st.header("Dashboard Insights")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Participants", len(df))
    col2.metric("Total Events", df['Event Name'].nunique())
    col3.metric("Total Colleges", df['College'].nunique())
    col4.metric("Average Rating", round(df['Rating'].mean(), 2))

    # Event Type
    fig5 = px.pie(df, names='Event Type',
                  title="Event Type Distribution")
    st.plotly_chart(fig5, use_container_width=True)

    # Revenue
    if 'Amount Paid' in df.columns:
        fig6 = px.bar(df.groupby('Event Name')['Amount Paid'].sum(),
                      title="Revenue by Event")
        st.plotly_chart(fig6, use_container_width=True)

    # Dataset Preview
    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)
