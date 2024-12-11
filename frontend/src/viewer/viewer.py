from kivy.app import App
from kivy.uix.video import Video
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
import requests
import os

class VideoScreen(Screen):
    source = StringProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.video = Video(allow_stretch=True)
        self.layout.add_widget(self.video)
        self.add_widget(self.layout)
        
    def on_source(self, instance, value):
        if value.startswith('http'):
            local_path = self._download_video(value)
            self.video.source = local_path
        else:
            self.video.source = value
        self.video.state = 'play'
            
    def _download_video(self, url):
        if not os.path.exists('video_cache'):
            os.makedirs('video_cache')
            
        local_filename = os.path.join('video_cache', url.split('/')[-1])
        
        if not os.path.exists(local_filename):
            response = requests.get(url, stream=True)
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return local_filename

class VideoViewer(App):
    def __init__(self, video_urls):
        super().__init__()
        self.video_urls = video_urls
        self.current_index = 0
        
    def build(self):
        self.sm = ScreenManager(transition=SwapTransition())
        self._create_screens()
        Window.bind(on_touch_up=self._on_touch_up)
        return self.sm
    
    def _create_screens(self):
        indices = [
            (self.current_index - 1) % len(self.video_urls),
            self.current_index,
            (self.current_index + 1) % len(self.video_urls)
        ]
        
        self.sm.clear_widgets()
        
        for i, idx in enumerate(indices):
            screen = VideoScreen(name=f'video_{i}')
            screen.source = self.video_urls[idx]
            self.sm.add_widget(screen)
            
        self.sm.current = 'video_1'
    
    def _on_touch_up(self, instance, touch):
        if hasattr(touch, 'dy'):
            if abs(touch.dy) > 50:
                if touch.dy > 0:
                    self.current_index = (self.current_index + 1) % len(self.video_urls)
                else:
                    self.current_index = (self.current_index - 1) % len(self.video_urls)
                self._create_screens()


def main():
    # Example usage:
    video_urls = [
        'https://vj-video.s3.us-east-1.amazonaws.com//612afec9-bcb2-47ca-807b-756d6e83b4b7/f4aa6faa-a7e3-438c-9392-7f58127125ec/video.mp4?AWSAccessKeyId=AKIATTF3CDVL4EYACA6F&Signature=2BczKZ4gQ6RFTeWZbP8LOIc9mZw%3D&Expires=1733963524',
        'https://vj-video.s3.us-east-1.amazonaws.com//612afec9-bcb2-47ca-807b-756d6e83b4b7/c59248ec-405e-4051-b872-a4dbde6a1442/video.mp4?AWSAccessKeyId=AKIATTF3CDVL4EYACA6F&Signature=lqfaBNGrYLOuk4n2x2ktcD5MK0w%3D&Expires=1733963524',
        'https://vj-video.s3.us-east-1.amazonaws.com//612afec9-bcb2-47ca-807b-756d6e83b4b7/48310b2a-5eaa-424b-bd1b-ed2c3a5a10d1/video.mp4?AWSAccessKeyId=AKIATTF3CDVL4EYACA6F&Signature=%2BDGio8SVBaTDbrLBbdP7FVlnsYk%3D&Expires=1733963524'
    ]
    
    # Or load from JSON file:
    # video_urls = load_video_urls('video_urls.json')
    
    VideoViewer(video_urls).run()

if __name__ == '__main__':
    main()