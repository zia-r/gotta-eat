import os
#from kivy.core.video.video_ffmpeg import VideoFFMpeg  # Add this import
#from kivy.core.video import Video as CoreVideo
import http.client
import json
import subprocess
import sys

serper_api_key = os.environ.get("SERPER_API_KEY", None)
if serper_api_key is None:
    with open(".env", "r") as r:
        for line in r:
            key, value = line.strip().split("=")
            if key == "SERPER_API_KEY":
                serper_api_key = value
                break

def main():
    # Example usage:
    restaurants = sys.argv[:1]
    video_urls = []
    conn = http.client.HTTPSConnection("google.serper.dev")
    for restaurant in restaurants:
        payload = json.dumps({
            "q": restaurant
        })
        headers = {
            'X-API-KEY': serper_api_key,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/videos", payload, headers)
        res = conn.getresponse()
        data = res.read()
        obj = json.loads(data.decode("utf-8"))
        print(obj)
        for video in obj["videos"][:1]:
            if "link" in video:
                video_urls.append({"restaurant": restaurant, 
                                   "video": video["link"]})
        conn.close()
    
    print(video_urls)

    counter = 0
    new_urls =[]
    for url in video_urls:
        subprocess.call(
            ["yt-dlp",
             "-f",
             "mp4",
             url["video"],
             "-o",
            f"video_cache/{counter}.mp4"]
        )
        new_urls.append({"restaurant": url["restaurant"],
                         "path": f"/Users/stankley/Development/gotta-eat/frontend/video_cache/{counter}.mp4"})
        counter += 1
    # Or load from JSON file:
    # video_urls = load_video_urls('video_urls.json')
    pairs = []
    for item in new_urls:
        pairs.extend([f'"{item["restaurant"]}"', item["path"]])

    files = " ".join(pairs)
    subprocess.call(f"../swifty-frontend/viewer {files}", shell=True)

if __name__ == '__main__':
    main()