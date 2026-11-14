import plotly.express as px 
import pandas as pd 

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def create_schedule_heatmap(df: pd.DataFrame): 
    """Generates day vs hour posting schedule heatmap based on average views.""" 
    pivot = df.pivot_table(
        index="day_of_week",
        columns="hour_published", 
        values="views",
        aggfunc="mean"
        ).reindex(DAY_ORDER).fillna(0)
    fig = px.imshow(
        pivot, 
        labels=dict(x="Hour of Day (UTC)", y="Day of Week", color="Avg Views"), 
        x =[f"{h:02d}:00" for h in pivot.columns], 
        y =pivot.index, 
        color_continuous_scale="Blues", 
        aspect="auto"
    ) 
    fig.update_layout(title="Average Views by Upload Schedule") 
    return fig
def create_keyword_chart(kw_df: pd.DataFrame): 
    """Generates horizontal bar chart for high-performing keywords.""" 
    if kw_df.empty: 
        return None
    fig = px.bar( 
        kw_df, 
        x ="avg_views", 
        y ="keyword", 
        orientation="h", 
        text="frequency", 
        color="performance_vs_avg (%)", 
        color_continuous_scale="Viridis", 
        labels={"avg_views": "Average Views", "keyword": "Title Keyword", "frequency":"Occurrences"}, 
        title="Top Title Keywords by Average Views") 
    fig.update_layout(yaxis={"categoryorder": "total ascending"}) 
    return fig