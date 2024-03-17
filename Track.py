import time
import logging
import pydub
from pydub.playback import play as pydub_play
from pydub import AudioSegment
from pydub.utils import make_chunks
from multiprocessing import Process
import threading
from eventdisp import EventDispatcher, Event
import enum
import pyaudio

logger = logging.getLogger(f"root___.weevil_.track__")
logger.info(f"Logging to file enabled.")


class TrackState(enum.Enum):
    Dispose = -1
    Play = 1
    Pause = 2
    Initiated = 3

class Track(EventDispatcher):


    def __init__(self, source:str=None, video=None, dB=0) -> None:
        super().__init__()
        logger.info("Begin Initiating Track")
        # Public 
        self.source = source
        self.video = video
        # Private
        self.__CHUNK_LEN = 64
        self.__i = 0
        self.__decibels_adjust = dB
        self.__audio = AudioSegment.from_file(source) if source else None
        self.__state = TrackState.Dispose       
        self.__output_stream = None
        self.__pyaudio = None
        self.__chunks = None
        logger.info("Finish preparing track for initiation.")


    def dispose(self): 
        if self.__state == TrackState.Dispose:
            raise Exception("Track is already disposed.")  

        self.__state = TrackState.Dispose
        self.__output_stream.stop_stream()
        self.__output_stream.close()
        self.__pyaudio.terminate()
        self.__pyaudio = None


    def initiate(self):
        if self.__state != TrackState.Dispose:
            raise Exception("Track is already initiated.")

        self.__state = TrackState.Pause
        self.__chunks = self.__audio[::self.__CHUNK_LEN]
        self.__pyaudio = pyaudio.PyAudio()
        self.__output_stream = self.__pyaudio.open(format=self.__pyaudio.get_format_from_width(self.__audio.sample_width),
                                      channels=self.__audio.channels,
                                      rate=self.__audio.frame_rate,
                                      output=True)
        def stream_write():
            for chunk in self.__chunks:
                # Prepare chunk volume
                chunk += self.__decibels_adjust

                # Return so the thread can be terminated
                if self.__state == TrackState.Dispose: return 0

                # Only continue the audio output we should
                while (self.__state == TrackState.Pause): 
                    # Return so the thread can be terminated
                    if self.__state == TrackState.Dispose: return 0
                    # Sleep 50ms before checking the state again
                    time.sleep(0.05)
                
                # Return so the thread can be terminated
                if self.__state == TrackState.Dispose: return 0

                # Playback audio
                self.__output_stream.write(chunk._data)

            # If we are out of audio data, the track has ended.
            self.dispatch(Event(name="track.end", data={"track":self}))

        # Start playback thread
        threading.Thread(target=stream_write, daemon=True).start()

        logger.info("Track initiated.")

        self.__state = TrackState.Initiated
        

    def play(self): 
        if self.is_disposed():
            raise Exception("Track is already disposed.")  

        if self.is_playing(): return

        self.__state =TrackState.Play


    def pause(self): 
        if self.is_disposed():
            raise Exception("Track is already disposed.")  

        if self.is_paused(): return

        self.__state = TrackState.Pause

    
    def is_disposed(self):
        return self.__state == TrackState.Dispose


    def get_current_time_ms(self):
        if self.is_disposed(): raise Exception("Track is already disposed.")  

        return self.__i * self.__CHUNK_LEN


    def get_duration_ms(self):
        return len(self.__audio)

    
    def seek(self, milliseconds):
        if self.is_disposed(): raise Exception("Track is already disposed.")  

        self.__i = milliseconds / self.__CHUNK_LEN


    def is_paused(self):
        if self.is_disposed(): raise Exception("Track is already disposed.")  

        return self.__state ==TrackState.Pause


    def is_playing(self):
        if self.is_disposed(): raise Exception("Track is already disposed.")  

        return self.__state ==TrackState.Play


    def set_volume(self, decibles):
        if self.is_disposed(): raise Exception("Track is already disposed.")  

        self.__decibels_adjust = decibles
        logger.info(f"Assign volume to track {self}: {self.__decibels_adjust}dB")
