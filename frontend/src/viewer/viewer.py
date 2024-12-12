from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
import os
import mpv

import os
import vlc
from kivy.properties import StringProperty
import asyncio
#from kivy.core.video.video_ffmpeg import VideoFFMpeg  # Add this import
#from kivy.core.video import Video as CoreVideo
import requests
import os
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import subprocess

serper_api_key = os.environ.get("SERPER_API_KEY", None)
# Set environment variable for video provider
os.environ['KIVY_VIDEO'] = 'ffpyplayer'

class MPVPlayer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = mpv.MPV(
            input_default_bindings=True,
            input_vo_keyboard=True,
            video_unscaled=True,
            loop='inf'
        )
        
    def play(self, filepath):
        self.player.play(filepath)
        
    def stop(self):
        self.player.stop()
        
    def pause(self):
        self.player.pause = True
        
    def resume(self):
        self.player.pause = False

class VideoScreen(Screen):
    source = StringProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.player = MPVPlayer()
        self.layout.add_widget(self.player)
        self.add_widget(self.layout)
        
    def on_source(self, instance, value):
        if value and os.path.exists(value):
            print(f"Loading video: {value}")
            self.player.play(value)
            
    def on_leave(self):
        self.player.stop()
        
    def on_enter(self):
        if self.source:
            self.player.play(self.source)

class VideoViewer(App):
    def __init__(self, video_files):
        super().__init__()
        self.video_files = video_files
        self.current_index = 0
    
    def build(self):
        self.sm = ScreenManager(transition=SwapTransition())
        self._create_screens()
        Window.bind(on_touch_up=self._on_touch_up)
        return self.sm
    
    def _create_screens(self):
        indices = [
            (self.current_index - 1) % len(self.video_files),
            self.current_index,
            (self.current_index + 1) % len(self.video_files)
        ]
        
        self.sm.clear_widgets()
        
        for i, idx in enumerate(indices):
            screen = VideoScreen(name=f'video_{i}')
            screen.source = self.video_files[idx]
            self.sm.add_widget(screen)
            
        self.sm.current = 'video_1'
    
    def _on_touch_up(self, instance, touch):
        if hasattr(touch, 'dy'):
            if abs(touch.dy) > 50:
                if touch.dy > 0:
                    self.current_index = (self.current_index + 1) % len(self.video_files)
                else:
                    self.current_index = (self.current_index - 1) % len(self.video_files)
                self._create_screens()
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
        obj = json.loads(data.decode("utf-8"))
        print(obj)
        for video in obj["videos"][:1]:
            if "link" in video:
                video_urls.append(video["link"])
        conn.close()
    
    print(video_urls)

    counter = 0
    new_urls =[]
    for url in video_urls:
        subprocess.call(
            ["yt-dlp",
             "-f",
             "mp4",
             url,
             "-o",
            f"video_cache/{counter}.mp4"]
        )
        new_urls.append(f"/Users/stankley/Development/gotta-eat/frontend/video_cache/{counter}.mp4")
        counter += 1
    # Or load from JSON file:
    # video_urls = load_video_urls('video_urls.json')
    
    VideoViewer(new_urls).run()

if __name__ == '__main__':
    main()