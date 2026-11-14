import os 
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
class YouTubeAPIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key not found. Please set YOUTUBE_API_KEY in .env")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
    def get_channel_info(self, handle: str): 
        """Resolves handle to channel details and uploads playlist ID.""" 
        clean_handle = handle.strip().replace("https://www.youtube.com/", "").replace("@", "")
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            forHandle=clean_handle
        ) 
        response = request.execute()
        if not response.get("items"):
            raise ValueError(f"Channel '{handle}' not found.")
        
        item = response["items"][0] 
        return { 
            "channel_id": item["id"], 
            "title": item["snippet"]["title"], 
            "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
            "total_videos": int(item["statistics"].get("videoCount", 0)), 
            "subscriber_count": int(item["statistics"].get("subscriberCount", 0))
        }

    def fetch_recent_videos(self, playlist_id: str, max_results: int = 500):
        """Fetches up to max_results videos in batches of 50 to conserve API quota."""
        video_ids = [] 
        next_page_token = None
        # Fetch Video IDs from Uploads Playlist 
        while len(video_ids) < max_results: 
            fetch_count = min(50, max_results - len(video_ids)) 
            request = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id, 
                maxResults=fetch_count, 
                pageToken=next_page_token
            ) 
            response = request.execute()
            for item in response.get("items", []): 
                video_ids.append(item["contentDetails"]["videoId"])
            next_page_token = response.get("nextPageToken") 
            if not next_page_token: 
                break

        # Batch Fetch Video Details (50 IDs per call) 
        video_data = [] 
        for i in range(0, len(video_ids), 50): 
            batch_ids = video_ids[i:i+50] 
            request = self.youtube.videos().list(
                part="snippet,statistics", 
                id=",".join(batch_ids)
            ) 
            response = request.execute()
            
            for item in response.get("items", []):
                snippet = item["snippet"] 
                stats = item.get("statistics", {}) 
                video_data.append({
                    "id": item["id"], 
                    "title": snippet["title"], 
                    "published_at": snippet["publishedAt"], 
                    "views": int(stats.get("viewCount", 0)), 
                    "likes": int(stats.get("likeCount", 0)), 
                    "comments": int(stats.get("commentCount", 0))
                })
        return video_data