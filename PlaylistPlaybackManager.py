import pytube 
import os 
import re 
import client
import logging
from VideoHelper import VideoHelper


# Create a logger object for the PlaylistPlaybackManager class
logger = logging.getLogger(f"root___.weevil_.playlis")
logger.info(f"Logging to file enabled.")


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
        self.path = output_folder         
        if not os.path.exists(self.path): os.makedirs(self.path)

        logger.info("PlaylistPlaybackManager initiated successfully. Playlist Title: %s", self.playlist.title)

    def fill(self):
        logger.info("Filling playlist...")
        for video in self.playlist.videos_generator():
            logger.debug("Adding video to playlist: %s", video.title)
            self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type))
        return self.videos 

    def yield_iterate(self, silent=False):
        logger.info("Iterating over playlist...")
        for video in self.playlist.videos_generator():
            logger.debug("Yielding next video from playlist: %s", video.title)
            self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type, silent))
            yield self.get_next(), video

    def get_prev(self) -> str | None:

        logger.debug("Retrieving previous video from playlist...")
        if self.current_mp > 0:
            self.current_mp -= 1
            return self.get_current()
        return None
    
    def get_next(self) -> str | None:
        logger.debug("Retrieving next video from playlist...")
        if self.current_mp < self.playlist.length:
            self.current_mp += 1
            return self.get_current()
        return None

    def has_next(self) -> bool:
        logger.debug("Checking if playlist has next video...")
        return self.current_mp < self.playlist.length - 1

    def get_current(self) -> str | None:
        logger.debug("Retrieving current video from playlist...")
        return self.videos[self.current_mp] if self.current_mp > 0 and self.current_mp < self.playlist.length else None
