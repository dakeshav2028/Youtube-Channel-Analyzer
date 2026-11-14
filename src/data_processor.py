import pandas as pd 
import re
from collections import Counter
STOPWORDS = { " a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
"as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", " can't", "cannot",
"could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", " down", "during", "each", "few", 
"for", "from", "further", "had", "hadn't", "has", "hasn't", "have", " haven't", "having", "he", "he'd", "he'll", 
"he's", "her", "here", "here's", "hers", "herself", "him", " himself", "his", "how", "how's", "i", "i'd", "i'll", 
"i'm", "i've", "if", "in", "into", "is", "isn't", " it", "it's", "its", "itself", "let's", "me", "more", "most", 
"mustn't", "my", "myself", "no", "nor", " not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", 
"ours", "ourselves", "out", " over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", 
"shouldn't", "so", "some", " such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", 
"then", "there", " there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", 
"through", "to", " too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
"we've", "were", " weren't", "what", "what's", "whatever", "when", "when's", "where", "where's", "which", 
"while","who"," who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", 
"you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "vs", "full", "video"
}

def process_video_dataframe(raw_data: list) -> pd.DataFrame: 
    """Transforms raw API dictionary into cleaned DataFrame with engineered metrics.""" 
    df = pd.DataFrame(raw_data) 
    if df.empty: 
        return df
    # Datetime conversions 
    df["published_at"] = pd.to_datetime(df["published_at"]) 
    df["day_of_week"] = df["published_at"].dt.day_name() 
    df["hour_published"] = df["published_at"].dt.hour
    
    # Engagement ratios
    df["like_ratio (%)"] = (df["likes"] / df["views"].replace(0, 1) * 100).round(2) 
    df["comment_ratio (%)"] = (df["comments"] / df["views"].replace(0, 1) * 100).round(2)
    return df
def extract_keyword_performance(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame: 
    """Mines titles for keywords and calculates mean views for each keyword.""" 
    word_views = {} 
    word_counts = Counter()
    for _, row in df.iterrows(): 
        title = row["title"].lower() 
        words = re.findall(r'\b[a-z0-9]+\b', title)
        filtered_words = set([w for w in words if w not in STOPWORDS and len(w) > 2 and not w.isdigit()])
    
        for word in filtered_words: 
            word_counts[word] += 1 
            if word not in word_views: 
                word_views[word] = []
            word_views[word].append(row["views"])
    # Aggregate keyword performance 
    keyword_stats = [] 
    channel_avg_views = df["views"].mean() if not df.empty else 0
    
    for word, count in word_counts.items(): 
        if count >= 3: # Only evaluate keywords used at least 3 times 
            avg_views = sum(word_views[word]) / len(word_views[word]) 
            keyword_stats.append({
                "keyword": word, 
                "frequency": count, 
                "avg_views": round(avg_views, 2), 
                "performance_vs_avg (%)": round(((avg_views - channel_avg_views)/channel_avg_views) * 100, 2) 
            })
    result_df = pd.DataFrame(keyword_stats) 
    if not result_df.empty: 
        return result_df.sort_values(by="avg_views", ascending=False).head(top_n)
    return pd.DataFrame(columns=["keyword", "frequency", "avg_views", "performance_vs_avg (%)"])
    