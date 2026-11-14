import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add the project directory to sys.path so 'src' imports work seamlessly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src.api_client import YouTubeAPIClient 
    from src.data_processor import process_video_dataframe, extract_keyword_performance 
    from src.visualizer import create_schedule_heatmap, create_keyword_chart
except ModuleNotFoundError:
    from api_client import YouTubeAPIClient 
    from data_processor import process_video_dataframe, extract_keyword_performance 
    from visualizer import create_schedule_heatmap, create_keyword_chart

st.set_page_config(page_title="YouTube Channel Analyzer", page_icon="📊", layout="wide")
st.title("📊 YouTube Channel Performance & Insights Analyzer") 
st.caption("Analyze upload timing, engagement trends, and title keyword strategies via official YouTube API.")

# Sidebar Controls 
st.sidebar.header("Search Channel") 
handle_input = st.sidebar.text_input("Enter YouTube Handle or URL:", value="@mkbhd") 
max_videos = st.sidebar.slider("Max Videos to Fetch:", min_value=50, max_value=500, value=200, step=50) 
analyze_btn = st.sidebar.button("Analyze Channel", type="primary")

if analyze_btn or handle_input: 
    try: 
        api_client = YouTubeAPIClient()
        
        with st.spinner("Fetching channel metadata..."): 
            channel_info = api_client.get_channel_info(handle_input)
        st.subheader(f"Results for **{channel_info['title']}**")

        # Display Channel Safeguard Info 
        c1, c2, c3 = st.columns(3) 
        c1.metric("Total Channel Uploads", f"{channel_info['total_videos']:,}") 
        c2.metric("Subscribers", f"{channel_info['subscriber_count']:,}") 
        c3.metric("Analyzing Recent Window", f"{min(max_videos, channel_info['total_videos'])}videos")

        # Fetch Video Data 
        with st.spinner("Extracting and processing video stats..."): 
            raw_videos = api_client.fetch_recent_videos( 
                channel_info["uploads_playlist_id"], 
                max_results=max_videos
            ) 
            df = process_video_dataframe(raw_videos)
        if df.empty: 
            st.warning("No public video data found for this channel.")
        else: 
            # Metric Cards 
            avg_views = int(df["views"].mean()) 
            avg_likes = int(df["likes"].mean()) 
            top_day = df.groupby("day_of_week")["views"].mean().idxmax()
            
            m1, m2, m3 = st.columns(3) 
            m1.metric("Average Views", f"{avg_views:,}") 
            m2.metric("Average Likes", f"{avg_likes:,}") 
            m3.metric("Best Performing Day", top_day)
            
            # Charts Layout 
            st.divider() 
            col_left, col_right = st.columns(2)
            
            with col_left: 
                st.plotly_chart(create_schedule_heatmap(df), use_container_width=True)
            with col_right: 
                kw_df = extract_keyword_performance(df) 
                kw_chart = create_keyword_chart(kw_df) 
                if kw_chart: 
                    st.plotly_chart(kw_chart, use_container_width=True)
                else: 
                    st.info("Not enough repeating keywords found in recent video titles.")
            # Raw Data Table 
            with st.expander("View Filtered Data Table"): 
                st.dataframe( 
                    df[["title", "published_at", "views", "likes", "comments", "like_ratio (%)"]], 
                    use_container_width=True
                )
    except Exception as e: 
        st.error(f"Error processing request: {str(e)}")