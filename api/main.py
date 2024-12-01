import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Dict

class YouTubeDownloader:
    def __init__(self, base_url="https://yt5s.biz/mates/en/convert", max_retries=3):
        self.base_url = base_url
        self.max_retries = max_retries
        self.headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://yt5s.biz",
            "referer": "https://yt5s.biz/enxj101/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        self.formats = {
            "mp3_128k": {
                "ext": "mp3",
                "note": "128k",
                "format": None,
                "download_key": "downloadUrlX",
            },
            "mp4_360p": {
                "ext": "mp4",
                "note": "360p",
                "format": "134",
                "download_key": "downloadUrlX",
            },
            "mp4_720p": {
                "ext": "mp4",
                "note": "720p",
                "format": "136",
                "download_key": "downloadUrlX",
            },
            "mp4_1080p": {
                "ext": "mp4",
                "note": "1080p60",
                "format": "299",
                "download_key": "downloadUrlX",
            },
        }

    def download(self, video_url: str, video_id: str, title: str, format_key: str) -> str:
        if format_key not in self.formats:
            return ""
        
        format_config = self.formats[format_key]
        download_key = format_config["download_key"]

        for attempt in range(self.max_retries):
            try:
                payload = {
                    "id": video_id,
                    "platform": "youtube",
                    "url": video_url,
                    "title": title,
                    "ext": format_config["ext"],
                    "note": format_config["note"],
                    "format": format_config["format"] or "",
                }
                self.headers["x-note"] = format_config["note"]
                response = requests.post(
                    self.base_url, headers=self.headers, data=payload
                )
                response_json = response.json()
                if (
                    response_json.get("status") == "success"
                    and download_key in response_json
                ):
                    return response_json[download_key]
                time.sleep(3)
            except Exception:
                time.sleep(3)
        return ""

class DownloadRequest(BaseModel):
    video_url: str
    title: str
    video_id: str = "ypwjF/ZPYN6kI06qjQn2C7dtkDtfZwhwUux5GAgxRbSUbEYH92ehW+4bV8+cy37Q4OAPwxKFOPwWgTuS93pyvCWeopjS4wKyMIpreLr4+O0="

app = FastAPI(
    title="YouTube Downloader API",
    description="API for downloading YouTube video in various formats",
    version="1.0.0"
)

downloader = YouTubeDownloader()

@app.post("/download", response_model=Dict[str, str])
async def download_video(request: DownloadRequest):
    """
    Download YouTube video in all predefined formats
    
    - **video_url**: Full YouTube video URL
    - **title**: Video title
    - **video_id**: Predefined video ID
    """
    try:
        # Predefined formats to try
        formats_to_try = ["mp3_128k", "mp4_360p", "mp4_720p", "mp4_1080p"]
        
        # Store download results
        results = {format_key: "" for format_key in formats_to_try}

        # Download each format
        for format_key in formats_to_try:
            download_url = downloader.download(
                request.video_url, 
                request.video_id, 
                request.title, 
                format_key
            )
            results[format_key] = download_url
            time.sleep(5)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {
        "status": "healthy",
        "service": "YouTube Downloader API",
        "version": "1.0.0"
    }

# To run the application:
# uvicorn main:app --reload