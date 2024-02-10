from pyglet.event import EventDispatcher
from mutagen.mp4 import MP4
import pyglet
import pytube, os, threading, re, enum, time, datetime
import settings, client
from pytube.exceptions import AgeRestrictedError
import pytube.exceptions as pyex
from ssl import SSLError
import ffmpeg
import shutil
import logging
from icecream import ic


class EndEvent:
    def __init__(self, track):
        self.track = track

class Track(EventDispatcher):
    def __init__(self, source:str=None) -> None:
        super().__init__()
        self.source = source
        self.player = pyglet.media.Player()
        if source is not None:
            self.player.queue(pyglet.media.load(source))
            self.player.push_handlers(on_eos=self.dispatch_end)

    def dispatch_end(self):
        ic("Dispatching end event")
        self.dispatch_event('on_end')

    def end(self) -> bool:
        ic("Skipping to end")
        self.player.seek(self.player.source.duration)
        self.player.play()
        self.dispatch_event('on_end')
        return True

Track.register_event_type('on_end')

