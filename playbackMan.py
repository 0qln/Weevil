import re 
import enum
import settings 
import client
import logging
from PlaylistPlaybackManager import PlaylistPlaybackManager
from VideoHelper import VideoHelper
import Track
import commons


logger = logging.getLogger(f"root___.weevil_.playbac")
logger.info(f"Logging to file enabled.")



class PlaybackManager:    
    def __init__(self):
        self.content_type = ContentType.NONE
        self.tracks = []
        self.current = -1    
        self.generator = None
        self.volume_db = float(settings.get("volume_db"))
        self.playlist_info = None
        self.should_load = False


    def reset(self = None) -> bool:
        logger.info("Resetting playback manager")

        if self is not None:
            self.content_type = ContentType.NONE
            for track in self.tracks:
                track.pause()
            self.tracks.clear()
            self.current = -1
            self.generator = None
            self.playlist_info = None
            self.should_load = False

        return True

    def load(self, settings) -> bool:

        if "quit" in settings:
            self.current = 0
            return True

        logger.info("Loading playback...")

        # Get url
        url = settings.get("url") or settings.get("commons") and commons.storage[settings["commons"]] 

        # Determine content type
        self.content_type = ContentType.get(url)
        logger.info(f"{self.content_type = }")

        try: 
            # Begin loading
            if self.content_type is ContentType.PLAYLIST: self.load_playlist(url, settings)
            if self.content_type is ContentType.VIDEO: self.load_video(url, settings)
            if self.content_type is ContentType.NONE: 
                client.warn("Invalid url.")
                return False
        except Exception as e: 
            logger.error(f"Error loading {self.content_type}: {e}")
            return False

        return True


    def __get_gen(self, iterator):
        for track_source, video in iterator:
            logger.info(f"Yielding new track: {track_source, video}")
            if track_source is None: 
                continue
            track = Track.Track(track_source, video)
            track.set_volume(decibles=self.volume_db)
            track.register("track.end", lambda e: self.skip())
            self.tracks.append(track)
            yield track


    def load_playlist(self, url, settings) -> bool:
        logger.info("Loading playlist...")
        self.playlist_info = PlaylistPlaybackManager(url, settings["output_folder"], settings["file_type"])
        self.generator = self.__get_gen(self.playlist_info.yield_iterate("silent" in settings))
        if "fetch" in settings:
            logger.debug("Fetch content")
            while next(self.generator) and self.current == -1:
                pass
            logger.debug(f"Stop fetching content: {self.generator=} | {next(self.generator)=} | {self.current}")
            
        else:
            logger.debug("Dont fetch content")
        return True


    def play_playlist(self, url, settings) -> bool:
        logger.info("Playing playlist...")
        if self.tracks or next(self.generator): 
            self.current = 0 
            self.get_current().play()
            self.announce_current()
        return True


    def load_video(self, url, settings) -> bool:
        logger.info("Loading track...")
        track_source, video = VideoHelper.create_playback(url, settings["output_folder"], settings["file_type"], "silent" in settings)
        if track_source is None: return True
        track = Track.Track(track_source, video)
        track.set_volume(decibles=self.volume_db)
        track.register("track.end", lambda e: self.skip())
        self.tracks.append(track)
        return True 


    def play_video(self, url, settings) -> bool:
        logger.info("Playing track...")        
        if self.tracks:
            self.current = 0
            self.get_current().play()
            self.announce_current()
        return True


    def play(self, settings) -> bool:
        # Get url
        url = settings.get("url") or settings.get("commons") and commons.storage[settings["commons"]] 

        if url is not None:
            # New playback requested
            logger.debug(f"URL specified: {url}")

            # Clear potentional old stuff
            if self.tracks: 
                self.get_current().pause()
                self.tracks.clear()

            # Load new stuff
            if not self.load(settings):
                # Return false if the url contents could not be loaded
                logger.warn("Could not load url contents.")
                return False

        try: 
            logger.info("Starting playback...")

            # Begin playback
            if self.content_type is ContentType.PLAYLIST: self.play_playlist(url, settings)
            if self.content_type is ContentType.VIDEO: self.play_video(url, settings)
            if self.content_type is ContentType.NONE: client.warn("Invalid url.")

        except Exception as e: 
            logger.error(f"Error playing {self.content_type}: {e}")
            return False

        return True


    def announce_current(self):
        logger.info("Announce track")
        t = self.get_current()
        message = VideoHelper.get_title(t.source)
        name = "Track" if self.content_type == ContentType.VIDEO else "Current Track"
        client.hail(name=name, message=message)


    def get_current(self) -> Track.Track | None:
        current = self.tracks[self.current] if 0 <= self.current < len(self.tracks) else None
        logger.info(f"Current track: {current}")
        return current

    def pause(self):
        logger.info("Pausing playback")
        if self.get_current() is None:
            return
        self.get_current().pause()

    def resume(self):
        logger.info("Resuming playback")
        if self.get_current() is None:
            return
        self.get_current().play()

    def prev(self):
        logger.info("Playing previous track")
        if self.get_current() is None or self.current < 0:
            return
        self.get_current().pause()
        self.current -= 1
        self.get_current().seek(0)
        self.get_current().play()
        self.announce_current()

    def skip(self):
        logger.info("Skipping to next track")
        if self.get_current() is None:
            return
        self.get_current().pause()
        # If there is no next track, try to generate one 
        if self.current + 1 == len(self.tracks):
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
        self.get_current().seek(0)
        self.get_current().play()
        self.announce_current()

    def set_volume(self, decibles) -> bool:
        logger.info(f"Setting volume to {decibles = }")
        self.volume_db = decibles
        for track in self.tracks:
            track.set_volume(decibles=decibles)
        return True


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1

    def get(content):
        if re.search(r"list=[0-9A-Za-z_-]+", content):
            return ContentType.PLAYLIST
        if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", content):
            return ContentType.VIDEO
        return ContentType.NONE

        

