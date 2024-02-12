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
from PlaylistPlaybackManager import PlaylistPlaybackManager
from VideoHelper import VideoHelper
from Track import Track  


logger = logging.getLogger(f"root___.weevil_.playbac")
logger.info(f"Logging to file enabled.")


class PlaybackManager:    
    def __init__(self):
        self.content_type = ContentType.NONE
        self.tracks = []
        self.current = -1    
        self.generator = None
        self.volume = int(settings.get("volume"))
        self.playlist_info = None


    def reset(self = None) -> bool:
        logger.info("Resetting playback manager")
        if self is not None:
            for track in self.tracks:
                track.player.pause()
                track.player.delete()
            self.tracks.clear()
            self.current = -1
            self.generator = None

        return True


    def play(self, settings) -> bool:
        logger.info("Starting playback")
        # get url
        import commons
        url = settings.get("url") or settings.get("commons") and commons.storage[settings["commons"]]

        # determine content type
        self.content_type = ContentType.NONE
        if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url):
            self.content_type = ContentType.VIDEO
        if re.search(r"list=[0-9A-Za-z_-]+", url):
            self.content_type = ContentType.PLAYLIST
        logger.info(f"Content type: {self.content_type}")

        if self.content_type is ContentType.PLAYLIST:
            try:
                logger.info("Playing playlist")
                playlist = PlaylistPlaybackManager(url, settings["output_folder"], settings["file_type"])
                self.playlist_info = playlist
                iterator = playlist.yield_iterate()
                if playlist.has_next():
                    def gen():
                        for track_source, video in iterator:
                            logger.info(f"Yielding new track: {track_source, video}")
                            if track_source is None:
                                continue
                            t = Track(track_source, video)
                            t.push_handlers(on_end=self.skip)
                            t.player.volume = self.volume / 100
                            self.tracks.append(t)
                            yield t
                    self.generator = gen()
                    t = next(self.generator)
                    self.current = 0 
                    self.get_current().player.play()
                    self.announce_current()
            except Exception as e: 
                logger.error(f"Error playing playlist: {e}")

        if self.content_type is ContentType.VIDEO:
            try: 
                logger.info("Playing video...")
                track_source, video = VideoHelper.create_playback(url, settings["output_folder"], settings["file_type"])
                if track_source is None:
                    return True
                t = Track(track_source, video)
                self.tracks.append(t)
                t.player.volume = self.volume / 100
                t.push_handlers(on_end=self.skip)
                self.current = 0
                self.get_current().player.play()
                self.announce_current()
            except Exception as e: 
                logger.error(f"Error playing video: {e}")

        try:
            pyglet.app.run()
        except Exception as e:
            pass

        return True

    def announce_current(self):
        logger.info("Announce track")
        t = self.get_current()
        message = VideoHelper.get_title(t.source)
        name = "Track" if self.content_type == ContentType.VIDEO else "Current Track"
        client.hail(name=name, message=message)


    def get_current(self) -> Track | None:
        current = self.tracks[self.current] if 0 <= self.current < len(self.tracks) else None
        logger.info(f"Current track: {current}")
        return current

    def pause(self):
        logger.info("Pausing playback")
        if self.get_current() is None:
            return
        self.get_current().player.pause()

    def resume(self):
        logger.info("Resuming playback")
        if self.get_current() is None:
            return
        self.get_current().player.play()

    def prev(self):
        logger.info("Playing previous track")
        if self.get_current() is None or self.current < 0:
            return
        self.get_current().player.pause()
        self.current -= 1
        self.get_current().player.seek(0)
        self.get_current().player.play()
        self.announce_current()

    def skip(self):
        logger.info("Skipping to next track")
        if self.get_current() is None:
            return
        self.get_current().player.pause()
        # If there is no next track, try to generate one 
        generateNew = self.current + 1 == len(self.tracks)
        if generateNew:
            if self.generator is None:
                # End of playlist
                return
            # New track needs to get generated
            next_track = next(self.generator, None)
            if next_track is None:
                # End of playlist
                return
        # Assign next track
        self.current += 1
        self.get_current().player.seek(0)
        self.get_current().player.play()
        self.announce_current()

    def set_volume(self, value) -> bool:
        logger.info(f"Setting volume to {value}")
        self.volume = value
        for track in self.tracks:
            track.player.volume = value / 100
        return True


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1

