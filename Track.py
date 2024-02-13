import pytube, os, threading, re, enum, time, datetime
import settings, client
import logging
import pydub
from pydub.playback import play as pydub_play
from pydub import AudioSegment
from multiprocessing import Process
from pyeventdispatcher import dispatch, Event

logger = logging.getLogger(f"root___.weevil_.track__")
logger.info(f"Logging to file enabled.")


class Track:

    def __init__(self, source:str=None, video=None) -> None:
        logger.info("Begin Initiating Track")
        # Public 
        self.source = source
        self.video = video
        # Private
        self.__audio = AudioSegment.from_file(source) if source else None
        self.__player = None 
        self.__timings = {
            "play_session_begin": None,
            "ms": 0
        }
        self.__volume = 1
        self.__decibels_adjust = 0
        logger.info("Finish Initiating Track")


    #TODO: 
    @staticmethod
    def __play_a_w_e(audio_seg, track):
        pydub_play(audio_seg)
        dispatch(Event(name="track.end", data={"track": track}))


    def play(self):
        if self.is_playing(): return
        logger.debug("Start new process for playback")
        new_audio = self.get_new_audio()
        self.__player = Process(target=pydub_play, args=(new_audio,))
        self.__player.start()
        self.__timings["play_session_begin"] = time.time_ns() / 1000000
        

    def pause(self):
        logger.info(f"Pause track {self}")
        logger.debug(f"Paused: {self.is_paused()}")
        if self.is_paused(): return
        self.__player.terminate()
        self.__player = None
        self.__timings["ms"] += time.time_ns() / 1000000 - self.__timings["play_session_begin"]


    def get_current_time_ms(self):
        result = self.__timings["ms"] 
        logger.debug(f"Current time: {result}ms (track: {self})")
        return result
        

    def get_new_audio(self) -> AudioSegment:
        logger.debug(f"Generate new sample of track {self}:")
        # Crop the original
        output = self.__audio[(self.get_current_time_ms() - len(self.__audio)):]

        # Adjust volume
        output += self.__decibels_adjust
        logger.debug(f"Assign volume: {self.__decibels_adjust}dB / {self.__volume*100}%")

        # Return output
        logger.debug(f"New sample succsefully generated.")
        return output


    def get_duration_ms(self):
        return len(self.__audio)

    
    def seek(self, milliseconds):
        # set time stamp
        self.__timings["begin"] = time.time_ns() / 1000000 - milliseconds
        self.__timings["end"] = None
        self.__timings["ms"] = milliseconds

        # Update player
        if not self.is_paused(): self.__reload()


    def is_paused(self):
        return self.__player is None


    def is_playing(self):
        return self.__player is not None

    
    def __reload(self):
        logger.debug(f"Begin reload track {self}")
        # Get new player 
        new_audio = self.get_new_audio()

        # Start playback
        logger.debug(f"Terminate player")
        self.__player.terminate()
        logger.debug(f"Create player")
        self.__player = Process(target=pydub_play, args=(new_audio,))
        logger.debug(f"Start player")
        self.__player.start()


    #TODO: fix this
    def set_volume(self, percentage):
        if percentage < 0 or percentage > 1:
            raise Exception("Argument exception: Percentage out of bounds.")

        self.__volume = percentage

        decibels_NULL = -120
        decibels_FULL = 0

        self.__decibels_adjust = decibels_NULL * (1 - percentage)

        logger.info(f"Assign volume to track {self}: {self.__decibels_adjust}dB / {percentage*100}%")
        
        # Update player
        if not self.is_paused(): self.__reload()



