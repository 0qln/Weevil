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
from VideoHelper import VideoHelper


class PlaylistPlaybackManager(object):
    
    def __init__(self, url, output_folder, file_type) -> None:
        self.stop = False
        self.playlist = pytube.Playlist(url)
        try:
            client.hail(name="Playlist", message=self.playlist.title)
        except KeyError as e:
            client.warn(message="Playlist information cannot be accessed")
            client.warn(message="Cannot create playback from Private Playlist or Youtube Mix.")
            raise e

        self.videos = [str]
        self.current_mp = 0
        self.preferred_file_type = file_type
        
        # Replace invalid characters with underscores in the playlist title
        sanitized_title = re.sub(r'[\\/:*?"<>|]', '_', self.playlist.title)
        self.path = output_folder + self.playlist.playlist_id + "\\" + sanitized_title + "\\"
        if not os.path.exists(self.path): 
            os.makedirs(self.path)
        ic("PlaylistPlaybackManager initiated successfully.")

    def fill(self):
        ic("FILL_ITERATE: Filling playlist")
        for video in self.playlist.videos_generator():
            ic("FILL: Adding video to playlist")
            self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type))
        return self.videos 

    def yield_iterate(self):
        ic("YIELD_ITERATE: Iterating over playlist")
        for video in self.playlist.videos_generator():
            ic("YIELD: Yielding next video from playlist")
            self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type))
            yield self.get_next()

    def get_prev(self) -> str | None:
        ic("GET_PREV: Retrieving previous video from playlist")
        if self.current_mp > 0:
            self.current_mp -= 1
            return self.get_current()
        return None
    
    def get_next(self) -> str | None:
        ic("GET_NEXT: Retrieving next video from playlist")
        if self.current_mp < self.playlist.length:
            self.current_mp += 1
            return self.get_current()
        return None

    def has_next(self) -> bool:
        ic("HAS_NEXT: Checking if playlist has next video")
        return self.current_mp < self.playlist.length - 1

    def get_current(self) -> str | None:
        ic("GET_CURRENT: Retrieving current video from playlist")
        return self.videos[self.current_mp] if self.current_mp > 0 and self.current_mp < self.playlist.length else None

