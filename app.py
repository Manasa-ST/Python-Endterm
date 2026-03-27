import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="GATEWAYS-2025 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

INDIA_GEOJSON_URL = (
    "https://gist.githubusercontent.com/jbrobst/"
    "56c13bbbf9d97d187fea01ca62ea5112/raw/"
    "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
)

STATE_MAPPING = {
    "TN": "Tamil Nadu", "KA": "Karnataka", "KL": "Kerala",
    "AP": "Andhra Pradesh", "TS": "Telangana", "MH": "Maharashtra",
    "GJ": "Gujarat", "UP": "Uttar Pradesh", "RJ": "Rajasthan",
    "WB": "West Bengal", "MP": "Madhya Pradesh", "DL": "Delhi",
    "HR": "Haryana", "PB": "Punjab", "BR": "Bihar", "OR": "Odisha",
    "AS": "Assam", "JK": "Jammu and Kashmir", "HP": "Himachal Pradesh",
    "UK": "Uttarakhand", "GA": "Goa", "CH": "Chandigarh",
    "JH": "Jharkhand", "CT": "Chhattisgarh",
}

POSITIVE_KW = {
    "excellent", "good", "great", "amazing", "fun", "well", "engaging",
    "interesting", "useful", "creative", "practical", "informative",
    "organized", "structured", "exposure", "learning",
}
NEGATIVE_KW = {
    "poor", "bad", "boring", "worst", "disappointing", "terrible",
    "awful", "dull", "improvement", "slight", "needs",
}

BAR_COLOR = "#4472C4"
CHART_TEMPLATE = "plotly_white"


@st.cache_data
def load_data(path="fest_dataset.csv"):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def get_sentiment(text):
    words = set(str(text).lower().split())
    pos = bool(words & POSITIVE_KW)
    neg = bool(words & NEGATIVE_KW)
    if pos and not neg:
        return "Positive"
    if neg and not pos:
        return "Negative"
    return "Neutral"


try:
    df_full = load_data("fest_dataset.csv")
except FileNotFoundError:
    st.error("fest_dataset.csv not found. Place it in the same folder as app.py and restart.")
    st.stop()

df_full["State"] = df_full["State"].replace(STATE_MAPPING)

st.title("GATEWAYS-2025 Participation Analysis Dashboard")
st.write(
    "This dashboard helps the organizing team understand how participants engaged "
    "with GATEWAYS-2025. You can filter by event, college, state, and rating to "
    "explore specific segments of the data."
)
st.divider()

st.sidebar.header("Filter Participants")
st.sidebar.markdown("---")

all_events = ["All Events"] + sorted(df_full["Event Name"].dropna().unique().tolist())
all_colleges = ["All Colleges"] + sorted(df_full["College"].dropna().unique().tolist())
all_states = ["All States"] + sorted(df_full["State"].dropna().unique().tolist())

sel_event = st.sidebar.selectbox("Select Event", all_events)
sel_college = st.sidebar.selectbox("Select College", all_colleges)
sel_state = st.sidebar.selectbox("Select State", all_states)

rating_min = int(df_full["Rating"].min())
rating_max = int(df_full["Rating"].max())
sel_rating = st.sidebar.slider("Rating Range", min_value=rating_min, max_value=rating_max, value=(rating_min, rating_max))

st.sidebar.markdown("---")
st.sidebar.caption("All charts and tables update based on the filters above.")

df = df_full.copy()
if sel_event != "All Events":
    df = df[df["Event Name"] == sel_event]
if sel_college != "All Colleges":
    df = df[df["College"] == sel_college]
if sel_state != "All States":
    df = df[df["State"] == sel_state]
df = df[(df["Rating"] >= sel_rating[0]) & (df["Rating"] <= sel_rating[1])]
df = df.copy()

if df.empty:
    st.warning("No participants match the selected filters. Please adjust the sidebar filters.")
    st.stop()

total_part = len(df)
top_event = df["Event Name"].value_counts().idxmax()
top_state = df["State"].value_counts().idxmax()
avg_rating = round(df["Rating"].mean(), 2)

st.subheader("Key Insights")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Participants", f"{total_part:,}")
k2.metric("Most Popular Event", top_event)
k3.metric("Top Participating State", top_state)
k4.metric("Average Rating", f"{avg_rating} / 5")

st.divider()

st.subheader("Dataset Preview")
info_col, table_col = st.columns([1, 3])
with info_col:
    st.metric("Total Rows", len(df))
    st.metric("Unique Events", df["Event Name"].nunique())
    st.metric("Unique Colleges", df["College"].nunique())
    st.metric("States Represented", df["State"].nunique())
with table_col:
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=260)

st.divider()

st.subheader("Participation Trends")

tab_event, tab_college, tab_etype = st.tabs(["Event-wise", "College-wise", "Event Type"])

with tab_event:
    if sel_event == "All Events":
        event_counts = df.groupby("Event Name").size().reset_index(name="Participants")
        event_counts = event_counts.sort_values("Participants", ascending=False)
        x_axis = "Event Name"
        chart_title = "Number of Participants per Event"
        x_label = "Event"
    else:
        event_counts = df.groupby("College").size().reset_index(name="Participants")
        event_counts = event_counts.sort_values("Participants", ascending=False)
        x_axis = "College"
        chart_title = f"Participants by College for {sel_event}"
        x_label = "College"

    fig_event = px.bar(
        event_counts,
        x=x_axis,
        y="Participants",
        text="Participants",
        title=chart_title,
        template=CHART_TEMPLATE,
        color_discrete_sequence=[BAR_COLOR],
    )
    fig_event.update_traces(textposition="outside", marker_line_width=0, marker_color=BAR_COLOR)
    fig_event.update_layout(
        showlegend=False,
        xaxis_title=x_label,
        yaxis_title="Number of Participants",
        bargap=0.35,
        yaxis=dict(rangemode="tozero"),
        font=dict(family="Arial", size=13),
    )
    st.plotly_chart(fig_event, use_container_width=True)

with tab_college:
    college_counts = df["College"].value_counts().reset_index()
    college_counts.columns = ["College", "Participants"]
    college_counts = college_counts.sort_values("Participants", ascending=True)

    fig_college = px.bar(
        college_counts,
        x="Participants",
        y="College",
        orientation="h",
        text="Participants",
        title="Number of Participants per College",
        template=CHART_TEMPLATE,
        color_discrete_sequence=[BAR_COLOR],
    )
    fig_college.update_traces(textposition="outside", marker_line_width=0, marker_color=BAR_COLOR)
    fig_college.update_layout(
        showlegend=False,
        xaxis_title="Number of Participants",
        yaxis_title="",
        yaxis={"categoryorder": "total ascending"},
        xaxis=dict(rangemode="tozero"),
        font=dict(family="Arial", size=13),
    )
    st.plotly_chart(fig_college, use_container_width=True)

with tab_etype:
    etype_counts = df["Event Type"].value_counts().reset_index()
    etype_counts.columns = ["Event Type", "Count"]

    fig_etype = px.pie(
        etype_counts,
        names="Event Type",
        values="Count",
        hole=0.45,
        title="Participation Split: Individual vs Group Events",
        color_discrete_sequence=["#4472C4", "#A9BEE8"],
    )
    fig_etype.update_traces(
        textinfo="label+value+percent",
        pull=[0.03] * len(etype_counts),
        textfont=dict(family="Arial", size=13),
    )
    fig_etype.update_layout(legend_title_text="Event Type", font=dict(family="Arial", size=13))
    st.plotly_chart(fig_etype, use_container_width=True)

st.divider()

st.subheader("State-wise Participation Across India")

state_counts = df.groupby("State").size().reset_index(name="Participants")

fig_map = px.choropleth(
    state_counts,
    geojson=INDIA_GEOJSON_URL,
    featureidkey="properties.ST_NM",
    locations="State",
    color="Participants",
    hover_name="State",
    hover_data={"Participants": True},
    title="State-wise Participation Across India",
    color_continuous_scale="Blues",
)
fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="white")
fig_map.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Participants", thickness=15, len=0.6),
    height=520,
    font=dict(family="Arial", size=13),
)
st.plotly_chart(fig_map, use_container_width=True)

st.caption("State-wise participant breakdown for the current filter selection")
st.dataframe(
    state_counts.sort_values("Participants", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=300,
)

st.divider()

st.subheader("Participant Feedback and Ratings Analysis")

all_rating_vals = list(range(rating_min, rating_max + 1))
rating_dist = df["Rating"].value_counts().reindex(all_rating_vals, fill_value=0).reset_index()
rating_dist.columns = ["Rating", "Count"]
rating_dist = rating_dist.sort_values("Rating")

fig_rating = px.bar(
    rating_dist,
    x="Rating",
    y="Count",
    text="Count",
    title=f"Ratings Distribution  (Average rating: {avg_rating} out of 5)",
    template=CHART_TEMPLATE,
    color_discrete_sequence=[BAR_COLOR],
)
fig_rating.update_traces(textposition="outside", marker_line_width=0, marker_color=BAR_COLOR)
fig_rating.update_layout(
    showlegend=False,
    xaxis=dict(tickmode="linear", title="Rating"),
    yaxis=dict(title="Number of Participants", rangemode="tozero"),
    bargap=0.4,
    font=dict(family="Arial", size=13),
)
st.plotly_chart(fig_rating, use_container_width=True)

wc_col, fb_col = st.columns(2)

with wc_col:
    st.markdown("**Most Common Words in Participant Feedback**")
    feedback_text = " ".join(df["Feedback on Fest"].dropna().astype(str).tolist())
    if feedback_text.strip():
        wc = WordCloud(
            width=700,
            height=360,
            background_color="white",
            colormap="Blues",
            max_words=60,
            collocations=False,
            min_font_size=10,
        ).generate(feedback_text)
        fig_wc, ax = plt.subplots(figsize=(7, 3.6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    else:
        st.info("No feedback text available for the current selection.")

with fb_col:
    st.markdown("**Frequency of Each Feedback Response**")
    fb_counts = df["Feedback on Fest"].value_counts().reset_index()
    fb_counts.columns = ["Feedback", "Count"]
    fb_counts = fb_counts.sort_values("Count", ascending=True)

    fig_fb = px.bar(
        fb_counts,
        x="Count",
        y="Feedback",
        orientation="h",
        text="Count",
        title="Feedback Response Count",
        template=CHART_TEMPLATE,
        color_discrete_sequence=[BAR_COLOR],
    )
    fig_fb.update_traces(textposition="outside", marker_line_width=0, marker_color=BAR_COLOR)
    fig_fb.update_layout(
        showlegend=False,
        xaxis_title="Number of Responses",
        yaxis_title="",
        yaxis={"categoryorder": "total ascending"},
        xaxis=dict(rangemode="tozero"),
        font=dict(family="Arial", size=12),
    )
    st.plotly_chart(fig_fb, use_container_width=True)

st.markdown("**Sentiment Analysis of Participant Feedback**")

df["Sentiment"] = df["Feedback on Fest"].apply(get_sentiment)
sent_counts = df["Sentiment"].value_counts().reset_index()
sent_counts.columns = ["Sentiment", "Count"]

COLOR_SENT = {"Positive": "#4472C4", "Neutral": "#A9BEE8", "Negative": "#D0D0D0"}

sent_pie_col, sent_bar_col = st.columns(2)

with sent_pie_col:
    fig_sent_pie = px.pie(
        sent_counts,
        names="Sentiment",
        values="Count",
        color="Sentiment",
        color_discrete_map=COLOR_SENT,
        hole=0.4,
        title="Sentiment Distribution",
    )
    fig_sent_pie.update_traces(
        textinfo="label+percent+value",
        pull=[0.04] * len(sent_counts),
        textfont=dict(family="Arial", size=13),
    )
    fig_sent_pie.update_layout(font=dict(family="Arial", size=13))
    st.plotly_chart(fig_sent_pie, use_container_width=True)

with sent_bar_col:
    fig_sent_bar = px.bar(
        sent_counts.sort_values("Count", ascending=False),
        x="Sentiment",
        y="Count",
        color="Sentiment",
        color_discrete_map=COLOR_SENT,
        text="Count",
        title="Sentiment Count",
        template=CHART_TEMPLATE,
    )
    fig_sent_bar.update_traces(textposition="outside", marker_line_width=0)
    fig_sent_bar.update_layout(
        showlegend=False,
        xaxis_title="Sentiment",
        yaxis_title="Number of Participants",
        bargap=0.4,
        yaxis=dict(rangemode="tozero"),
        font=dict(family="Arial", size=13),
    )
    st.plotly_chart(fig_sent_bar, use_container_width=True)

st.markdown("**Average Rating by Event**")
avg_by_event = (
    df.groupby("Event Name")["Rating"]
    .mean()
    .round(2)
    .reset_index()
    .sort_values("Rating", ascending=False)
)
avg_by_event.columns = ["Event Name", "Average Rating"]

fig_avg_event = px.bar(
    avg_by_event,
    x="Event Name",
    y="Average Rating",
    text="Average Rating",
    title="Average Participant Rating per Event",
    template=CHART_TEMPLATE,
    color_discrete_sequence=[BAR_COLOR],
)
fig_avg_event.update_traces(textposition="outside", marker_line_width=0, marker_color=BAR_COLOR)
fig_avg_event.update_layout(
    showlegend=False,
    xaxis_title="Event",
    yaxis_title="Average Rating",
    bargap=0.35,
    yaxis=dict(range=[0, 5.5]),
    font=dict(family="Arial", size=13),
)
st.plotly_chart(fig_avg_event, use_container_width=True)

st.divider()

if "Amount Paid" in df.columns:
    st.subheader("Registration Fee Analysis")
    amt1, amt2 = st.columns(2)

    with amt1:
        amt_event = (
            df.groupby("Event Name")["Amount Paid"]
            .sum()
            .reset_index()
            .sort_values("Amount Paid", ascending=False)
        )
        amt_event.columns = ["Event Name", "Total Amount (Rs)"]

        fig_amt_event = px.bar(
            amt_event,
            x="Event Name",
            y="Total Amount (Rs)",
            text="Total Amount (Rs)",
            title="Total Registration Fee per Event",
            template=CHART_TEMPLATE,
            color_discrete_sequence=[BAR_COLOR],
        )
        fig_amt_event.update_traces(
            texttemplate="Rs %{text:,}", textposition="outside",
            marker_line_width=0, marker_color=BAR_COLOR
        )
        fig_amt_event.update_layout(
            showlegend=False,
            xaxis_title="Event",
            yaxis_title="Total Amount (Rs)",
            bargap=0.35,
            yaxis=dict(rangemode="tozero"),
            font=dict(family="Arial", size=13),
        )
        st.plotly_chart(fig_amt_event, use_container_width=True)

    with amt2:
        amt_state = (
            df.groupby("State")["Amount Paid"]
            .sum()
            .reset_index()
            .sort_values("Amount Paid", ascending=False)
        )
        amt_state.columns = ["State", "Total Amount (Rs)"]

        fig_amt_state = px.bar(
            amt_state,
            x="State",
            y="Total Amount (Rs)",
            text="Total Amount (Rs)",
            title="Total Registration Fee per State",
            template=CHART_TEMPLATE,
            color_discrete_sequence=[BAR_COLOR],
        )
        fig_amt_state.update_traces(
            texttemplate="Rs %{text:,}", textposition="outside",
            marker_line_width=0, marker_color=BAR_COLOR
        )
        fig_amt_state.update_layout(
            showlegend=False,
            xaxis_title="State",
            yaxis_title="Total Amount (Rs)",
            bargap=0.35,
            yaxis=dict(rangemode="tozero"),
            font=dict(family="Arial", size=13),
        )
        st.plotly_chart(fig_amt_state, use_container_width=True)

    st.divider()

st.subheader("Export Filtered Data")
export_df = df.drop(columns=["Sentiment"], errors="ignore")
csv_bytes = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Dataset as CSV",
    data=csv_bytes,
    file_name="gateways2025_filtered.csv",
    mime="text/csv",
)

st.divider()
st.markdown(
    "<center>Developed by Website Development Team — GATEWAYS-2025</center>",
    unsafe_allow_html=True,
)
