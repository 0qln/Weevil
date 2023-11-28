import vlc, time, enum, threading, os
from icecream import ic


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
        self.vlc_mediaPlayer:vlc.MediaPlayer = None
        self.on_state_change = threading.Event()
        self.title:str = None
        self.length:int = None
        self.decay_thread:threading.Thread = None


    def set_state(self, value:MediaPlayerState) -> MediaPlayerState:
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
        ic(self.set_state(MediaPlayerState.PLAYING))
        ic(self.vlc_mediaPlayer.play())

        def decay_state():
            # wait for it to start playing
            while (self.vlc_mediaPlayer.is_playing() != 1 and
                MediaPlayerState.STOPPED != self.state):
                time.sleep(0.05)
            # wait for playback to finish
            while (self.vlc_mediaPlayer.is_playing() == 1 or 
                self.state == MediaPlayerState.PAUSED):
                time.sleep(0.05)
            # handle a stop
            ic(self.stop())

        if self.decay_thread is None:
            self.decay_thread = threading.Thread(target=decay_state, args=[], daemon=True)
            self.decay_thread.start()      
            ic(self.decay_thread)

    def load(self, mediaSource, title=None, length=None) -> None:
        self.title = title
        self.length = length
        if self.vlc_mediaPlayer is not None: self.vlc_mediaPlayer.release()
        self.vlc_mediaPlayer = vlc.Instance().media_player_new()
        self.vlc_mediaPlayer.set_media(vlc.Instance().media_new(mediaSource))
        ic(self.set_state(MediaPlayerState.LOADED))

    def next(self) -> None:
        ic(self.set_state(MediaPlayerState.SKIPPING))
        if (self.vlc_mediaPlayer is not None):
            self.vlc_mediaPlayer.set_pause(1)

    def prev(self) -> None:
        ic(self.set_state(MediaPlayerState.ROLL_BACK))
        self.vlc_mediaPlayer.set_pause(1)

    def pause(self) -> None:
        ic(self.set_state(MediaPlayerState.PAUSED))
        self.vlc_mediaPlayer.set_pause(1)

    def resume(self) -> None:
        ic(self.set_state(MediaPlayerState.PLAYING))
        self.vlc_mediaPlayer.set_pause(0)
        # TODO: Find the underlying issue and create an actual fix
        # Quick fix for https://github.com/0qln/Weevil/issues/7  
        # time.sleep(0.003)
        # empty_line = " " * os.get_terminal_size().columns
        # for _ in range(2): print(f"\033[A{empty_line}\033[A")

    def set_volume(self, value) -> bool:
        result = -1
        if (self.vlc_mediaPlayer is not None):
            result = self.vlc_mediaPlayer.audio_set_volume(int(value))
        return result == 0

    def get_volume(self) -> int:
        result = self.vlc_mediaPlayer.audio_get_volume()
        return result

    def stop(self) -> None:
        ic(self.set_state(MediaPlayerState.STOPPED))
        if (self.vlc_mediaPlayer is not None):
            self.vlc_mediaPlayer.set_pause(1)
    
    def get_duration(self) -> int:
        return self.length

    def get_content_title(self) -> str:
        return self.title