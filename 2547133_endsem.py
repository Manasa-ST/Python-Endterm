import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
import matplotlib.pyplot as plt

# Load data

df = pd.read_csv('C5-FestDataset - fest_dataset.csv')


#df = load_data()

# Title
st.title("GATEWAYS-2025 Fest Analysis Dashboard")

# Sidebar for filters
st.sidebar.header("Filters")

# State filter
states = df['State'].unique()
selected_states = st.sidebar.multiselect("Select States", states, default=states)

# Event filter
events = df['Event Name'].unique()
selected_events = st.sidebar.multiselect("Select Events", events, default=events)

# Filter data
filtered_df = df[(df['State'].isin(selected_states)) & (df['Event Name'].isin(selected_events))]

# Create tabs
tab1, tab2, tab3 = st.tabs(["Participation Trends", "Feedback Analysis", "Dashboard Insights"])

with tab1:
    st.header("Participation Trends")

    # Event-wise participation
    st.subheader("Event-wise Participation")
    event_counts = filtered_df['Event Name'].value_counts()
    fig_event = px.bar(event_counts, x=event_counts.index, y=event_counts.values,
                       labels={'x': 'Event Name', 'y': 'Number of Participants'},
                       title="Participants per Event")
    st.plotly_chart(fig_event)

    # College-wise participation
    st.subheader("College-wise Participation")
    college_counts = filtered_df['College'].value_counts().head(10)  # Top 10
    fig_college = px.bar(college_counts, x=college_counts.index, y=college_counts.values,
                         labels={'x': 'College', 'y': 'Number of Participants'},
                         title="Top 10 Colleges by Participation")
    st.plotly_chart(fig_college)

    # State-wise participation
    st.subheader("State-wise Participation")

    # Use filtered data for the bar chart, but full India data for the map (ensures full-country view)
    state_counts = filtered_df['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Participants']
    state_counts_full = df['State'].value_counts().reset_index()
    state_counts_full.columns = ['State', 'Participants']

    # Bar chart for states (filtered)
    fig_bar = px.bar(state_counts, x='State', y='Participants',
                     labels={'State': 'State', 'Participants': 'Number of Participants'},
                     title="Participants by State")
    st.plotly_chart(fig_bar)

    # India map for state-wise participants using geojson (full India view)
    india_geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/india_states.geojson"
    india_geojson = None
    try:
        import requests
        response = requests.get(india_geojson_url, timeout=10)
        if response.ok:
            india_geojson = response.json()
    except Exception as e:
        st.warning(f"Could not load India geojson for map: {e}")

    if india_geojson is not None:
        fig_map = px.choropleth(state_counts_full,
                                geojson=india_geojson,
                                featureidkey='properties.NAME_1',
                                locations='State',
                                color='Participants',
                                projection='mercator',
                                title='State-wise Participants in India (Full)',
                                color_continuous_scale='Blues')
        fig_map.update_geos(fitbounds='locations', visible=False,
                            lataxis_range=[6, 38], lonaxis_range=[68, 98],
                            showcountries=False, showcoastlines=False,
                            showland=True, landcolor='lightgray')
        fig_map.update_layout(margin={'r':0,'t':30,'l':0,'b':0})
        st.plotly_chart(fig_map)
    else:
        st.info('India map not available; showing bar chart only.')

with tab2:
    st.header("Feedback Analysis")

    # Ratings distribution
    st.subheader("Rating Distribution")
    rating_counts = filtered_df['Rating'].value_counts().sort_index()
    fig_rating = px.bar(rating_counts, x=rating_counts.index, y=rating_counts.values,
                        labels={'x': 'Rating', 'y': 'Count'},
                        title="Distribution of Ratings")
    st.plotly_chart(fig_rating)

    # Average rating
    avg_rating = filtered_df['Rating'].mean()
    st.metric("Average Rating", f"{avg_rating:.2f}")

    # Sentiment analysis on feedback
    st.subheader("Feedback Sentiment Analysis")
    feedbacks = filtered_df['Feedback on Fest'].dropna()

    sentiments = []
    for feedback in feedbacks:
        blob = TextBlob(feedback)
        sentiment = blob.sentiment.polarity
        sentiments.append(sentiment)

    sentiment_df = pd.DataFrame({'Feedback': feedbacks, 'Sentiment': sentiments})
    sentiment_df['Sentiment Label'] = sentiment_df['Sentiment'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))

    sentiment_counts = sentiment_df['Sentiment Label'].value_counts()
    fig_sentiment = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                           title="Sentiment Distribution of Feedback")
    st.plotly_chart(fig_sentiment)

    # Show sample feedbacks
    st.subheader("Sample Feedbacks")
    st.dataframe(sentiment_df[['Feedback', 'Sentiment Label']].head(10))

with tab3:
    st.header("Dashboard Insights")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Participants", len(filtered_df))
    with col2:
        st.metric("Total Events", len(filtered_df['Event Name'].unique()))
    with col3:
        st.metric("Total Colleges", len(filtered_df['College'].unique()))
    with col4:
        st.metric("Average Rating", f"{filtered_df['Rating'].mean():.2f}")

    # Additional insights
    st.subheader("Event Type Distribution")
    event_type_counts = filtered_df['Event Type'].value_counts()
    fig_event_type = px.pie(event_type_counts, values=event_type_counts.values, names=event_type_counts.index,
                            title="Event Type Distribution")
    st.plotly_chart(fig_event_type)

    # Amount Paid Analysis
    st.subheader("Amount Paid Distribution")
    fig_amount = px.histogram(filtered_df, x='Amount Paid', nbins=10,
                              title="Distribution of Amount Paid")
    st.plotly_chart(fig_amount)

    # Revenue by Event
    st.subheader("Revenue by Event")
    revenue_event = filtered_df.groupby('Event Name')['Amount Paid'].sum().reset_index()
    fig_revenue = px.bar(revenue_event, x='Event Name', y='Amount Paid',
                         title="Total Revenue by Event")
    st.plotly_chart(fig_revenue)