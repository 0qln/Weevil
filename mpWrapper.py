import vlc, time, enum, threading
from icecream import ic


class MediaPlayerState(enum.Enum):
    NONE = -1
    PAUSED = 1
    PLAYING = 2
    STOPPED = 3
    SKIPPING = 4


class MediaPlayer:
    def __init__(self) -> None:
        self.state = MediaPlayerState.NONE
        self.vlc_mediaPlayer = None


    def play(self) -> None:
        self.vlc_mediaPlayer.play()

    def load(self, mediaSource) -> None:
        self.vlc_mediaPlayer = vlc.Instance().media_player_new()
        self.vlc_mediaPlayer.set_media(vlc.Instance().media_new(mediaSource))

    def skip(self) -> None:
        self.state = MediaPlayerState.SKIPPING
        self.vlc_mediaPlayer.set_pause(1)

    def reset(self) -> None:
        self.state = MediaPlayerState.NONE
        self.vlc_mediaPlayer = None

    def pause(self) -> None:
        self.state = MediaPlayerState.PAUSED
        self.vlc_mediaPlayer.set_pause(1)

    def resume(self) -> None:
        self.state = MediaPlayerState.PLAYING
        self.vlc_mediaPlayer.set_pause(0)
        # deactivate `MediaPlayerState.PLAYING` when media has finished
        threading.Thread(target=self.decay_state, daemon=True).start()

    def toggle_pause(self) -> None:
        if self.is_playing():
            self.pause()
        else:
            self.resume()            

    def stop(self) -> None:
        self.state = MediaPlayerState.STOPPED
        self.vlc_mediaPlayer.set_pause(1)


    def is_playing(self) -> bool:
        return self.state == MediaPlayerState.PLAYING
        
    def decay_state(self) -> None:
        time.sleep(0.1)        
        while self.vlc_mediaPlayer.is_playing() == 1:
            time.sleep(0.1)
        if (self.state == MediaPlayerState.PLAYING):
            self.state = MediaPlayerState.NONE
            ic(self.state)
        return