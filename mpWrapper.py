import vlc, time


class MediaPlayer:
    def __init__(self, vlc_MediaPlayer) -> None:
        self.paused = False
        self.vlc_mediaPlayer = vlc_MediaPlayer

    def play(self):
        self.paused = False
        self.vlc_mediaPlayer.play()

    def pause(self):
        self.paused = True
        self.vlc_mediaPlayer.set_pause(69)

    def resume(self):
        self.paused = False
        self.vlc_mediaPlayer.set_pause(0)

    def stop(self):
        self.paused = False
        self.vlc_mediaPlayer.stop()

    def is_playing(self) -> bool:
        is_playing = self.vlc_mediaPlayer.is_playing() == 1
        is_paused = self.paused
        return (is_playing or is_paused)
    
    def wait_for_stop(self):        
        while self.is_playing() == True:
            time.sleep(0.1)
        return