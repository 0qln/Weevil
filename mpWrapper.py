import vlc, time, enum, threading
from icecream import ic


class MediaPlayerState(enum.Enum):
    NONE = -1
    PAUSED = 1
    PLAYING = 2
    STOPPED = 3
    SKIPPING = 4
    LOADED = 5



class MediaPlayer:
    def __init__(self) -> None:
        self.state = MediaPlayerState.NONE
        self.vlc_mediaPlayer = None
        self.on_state_change = threading.Event()


    def set_state(self, value:MediaPlayerState) -> None:
        self.state = value
        self.on_state_change.set()

    def get_state_once(self) -> MediaPlayerState:
        self.on_state_change.clear()
        return self.state

    def get_new_state(self) -> MediaPlayerState:
        self.on_state_change.wait()
        return self.get_state_once()
        


    def play(self) -> None:
        self.set_state(MediaPlayerState.PLAYING)
        self.vlc_mediaPlayer.play()

        def decay_state():
            while (self.vlc_mediaPlayer.is_playing() != 1 and
                MediaPlayerState.STOPPED != self.state):
                # wait for it to start playing
                time.sleep(0.05)
                pass
            while (self.vlc_mediaPlayer.is_playing() == 1 and 
                   MediaPlayerState.STOPPED != self.state):
                # wait for playback to finish
                time.sleep(0.05)
            # handle a stop
            ic(self.stop())

        threading.Thread(target=decay_state, args=[], daemon=True).start()
        
        

    def load(self, mediaSource) -> None:
        if self.vlc_mediaPlayer is not None: self.vlc_mediaPlayer.release()
        self.vlc_mediaPlayer = vlc.Instance().media_player_new()
        self.vlc_mediaPlayer.set_media(vlc.Instance().media_new(mediaSource))
        self.set_state(MediaPlayerState.LOADED)

    # TODO: `get_time()` `set_time()`
    # `get_time()` seems broken, does not update regualy
    def skip(self) -> None:
        self.set_state(MediaPlayerState.SKIPPING)
        self.vlc_mediaPlayer.set_pause(1)

    def pause(self) -> None:
        self.set_state(MediaPlayerState.PAUSED)
        self.vlc_mediaPlayer.set_pause(1)

    def resume(self) -> None:
        self.set_state(MediaPlayerState.PLAYING)
        self.vlc_mediaPlayer.set_pause(0)

    def toggle_pause(self) -> None:
        if self.is_playing():
            self.pause()
        else:
            self.resume()            

    def stop(self) -> None:
        self.set_state(MediaPlayerState.STOPPED)
        self.vlc_mediaPlayer.set_pause(1)
        self.vlc_mediaPlayer.release()
    
        
