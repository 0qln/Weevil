import enum
import threading
import time
import pyglet
import os
from icecream import ic
import settings

class MediaPlayerState(enum.Enum):
    NONE = -1
    PAUSED = 1
    PLAYING = 2
    STOPPED = 3
    SKIPPING = 4
    LOADED = 5
    ROLL_BACK = 6

class MediaPlayer:
    def __init__(self) -> None:
        self.state = MediaPlayerState.NONE
        self.player = None
        self.on_state_change = threading.Event()
        self.title = None
        self.length = None
        self.decay_thread = None

    def set_state(self, value: MediaPlayerState) -> MediaPlayerState:
        self.state = value
        self.on_state_change.set()
        return value

    def get_state_once(self) -> MediaPlayerState:
        self.on_state_change.clear()
        return self.state

    def get_new_state(self) -> MediaPlayerState:
        self.on_state_change.wait()
        return self.get_state_once()

    def play(self) -> None:
        if self.player is None:
            return
        
        ic(self.set_state(MediaPlayerState.PLAYING))
        self.player.play()

        def decay_state():
            while self.player.playing != 1 and self.state != MediaPlayerState.STOPPED:
                time.sleep(0.05)
            
            while self.player.playing == 1 or self.state == MediaPlayerState.PAUSED:
                time.sleep(0.05)
            
            ic(self.stop())

        if self.decay_thread is None:
            self.decay_thread = threading.Thread(target=decay_state, args=[], daemon=True)
            self.decay_thread.start()
            ic(self.decay_thread)

    def load(self, mediaSource, title=None, length=None) -> None:
        self.title = title
        self.length = length
        self.player = pyglet.media.Player()
        source = pyglet.media.load(mediaSource)
        self.player.queue(source)
        ic(self.set_state(MediaPlayerState.LOADED))
        ic(settings.get("volume"))
        self.set_volume(int(settings.get("volume")))

    def next(self) -> None:
        ic(self.set_state(MediaPlayerState.SKIPPING))
        if self.player is not None:
            self.player.pause()

    def prev(self) -> None:
        ic(self.set_state(MediaPlayerState.ROLL_BACK))
        if self.player is not None:
            self.player.pause()

    def pause(self) -> None:
        ic(self.set_state(MediaPlayerState.PAUSED))
        if self.player is not None:
            self.player.pause()

    def resume(self) -> None:
        ic(self.set_state(MediaPlayerState.PLAYING))
        if self.player is not None:
            self.player.play()

    def set_volume(self, value) -> bool:
        if self.player is not None:
            self.player.volume = value / 100
            return True
        return False

    def get_volume(self) -> int:
        if self.player is not None:
            return int(self.player.volume * 100)
        return -1

    def stop(self) -> None:
        ic(self.set_state(MediaPlayerState.STOPPED))
        if self.player is not None:
            self.player.pause()

    def get_duration(self) -> int:
        return self.length

    def get_content_title(self) -> str:
        return self.title
