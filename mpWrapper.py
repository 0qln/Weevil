import vlc, time, enum


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

    def play(self, mediaSource) -> None:
        self.state = MediaPlayerState.PLAYING
        self.vlc_mediaPlayer = vlc.Instance().media_player_new()
        self.vlc_mediaPlayer.set_media(vlc.Instance().media_new(mediaSource))
        self.vlc_mediaPlayer.play()

    def skip(self) -> None:
        self.state = MediaPlayerState.SKIPPING
        self.vlc_mediaPlayer.set_pause(69)

    def reset(self) -> None:
        self.state = MediaPlayerState.NONE
        self.vlc_mediaPlayer = None

    def pause(self) -> None:
        self.state = MediaPlayerState.PAUSED
        self.vlc_mediaPlayer.set_pause(69)

    def resume(self) -> None:
        self.state = MediaPlayerState.PLAYING
        self.vlc_mediaPlayer.set_pause(0)

    def stop(self) -> None:
        self.state = MediaPlayerState.STOPPED
        self.vlc_mediaPlayer.set_pause(69)

    def is_playing(self) -> bool:
        return self.state == MediaPlayerState.PLAYING
        
    
    def wait_for_stop(self) -> None:        
        while self.is_playing() == True:
            time.sleep(0.1)
        return