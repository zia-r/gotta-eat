from kivy.app import App
from kivy.uix.video import Video
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.clock import Clock
from TikTokApi import TikTokApi
from playwright.async_api import async_playwright
import asyncio
import requests
import os
from concurrent.futures import ThreadPoolExecutor
import http.client
import json

serper_api_key = os.environ.get("SERPER_API_KEY", None)

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Loading Videos...'))
        self.add_widget(layout)

class VideoScreen(Screen):
    source = StringProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.video = Video(allow_stretch=True)
        self.layout.add_widget(self.video)
        self.add_widget(self.layout)
        
    def on_source(self, instance, value):
        if value:
            self.video.source = value
            self.video.state = 'play'

class VideoViewer(App):
    def __init__(self, video_urls):
        super().__init__()
        self.video_urls = video_urls
        self.current_index = 0
        self.downloaded_videos = {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def build(self):
        self.sm = ScreenManager(transition=SwapTransition())
        loading_screen = LoadingScreen(name='loading')
        self.sm.add_widget(loading_screen)
        Clock.schedule_once(self.start_downloads, 0.1)
        Window.bind(on_touch_up=self._on_touch_up)
        return self.sm
    
    def download_video(self, url):
        if not os.path.exists('video_cache'):
            os.makedirs('video_cache')
            
        local_filename = os.path.join('video_cache', url.split('/')[-1])
        
        if not os.path.exists(local_filename):
            try:
                response = requests.get(url, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                with open(local_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                return None
                
        return local_filename
    
    def start_downloads(self, dt):
        futures = []
        for url in self.video_urls:
            future = self.executor.submit(self.download_video, url)
            futures.append((url, future))
        
        Clock.schedule_interval(lambda dt: self.check_downloads(futures), 0.5)
    
    def check_downloads(self, futures):
        all_complete = True
        for url, future in futures:
            if future.done():
                result = future.result()
                if result:
                    self.downloaded_videos[url] = result
            else:
                all_complete = False
        
        if all_complete and self.downloaded_videos:
            self._create_screens()
            return False
        return True
    
    def _create_screens(self):
        self.sm.clear_widgets()  # Remove loading screen
        
        if not self.downloaded_videos:
            print("No videos were downloaded successfully")
            return

        # Create all screens first
        for i, url in enumerate(self.video_urls):
            if url in self.downloaded_videos:
                screen = VideoScreen(name=f'video_{i}')
                screen.source = self.downloaded_videos[url]
                self.sm.add_widget(screen)

        # Switch to first video if we have any
        if self.sm.screens:
            self.sm.current = 'video_0'  # Start with first video
    
    def _on_touch_up(self, instance, touch):
        if not hasattr(touch, 'dy') or not self.sm.screens:
            return
            
        if abs(touch.dy) > 50:
            total_screens = len(self.sm.screens)
            if total_screens > 0:
                current_idx = int(self.sm.current.split('_')[1])
                if touch.dy > 0:  # Swipe up
                    next_idx = (current_idx + 1) % total_screens
                else:  # Swipe down
                    next_idx = (current_idx - 1) % total_screens
                self.sm.current = f'video_{next_idx}'
    
    def on_stop(self):
        self.executor.shutdown(wait=False)



def main():
    # Example usage:

    restaurants = ["Dhamaka New York", "Adda New York"]
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
        print(data.decode("utf-8"))

    # Or load from JSON file:
    # video_urls = load_video_urls('video_urls.json')
    
    VideoViewer(video_urls).run()

if __name__ == '__main__':
    main()