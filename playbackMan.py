from pyglet.event import EventDispatcher
from mutagen.mp4 import MP4
import pyglet
import pytube, os, threading, re, enum, time, datetime
from icecream import ic
import settings, client
from pytube.exceptions import AgeRestrictedError
import pytube.exceptions as pyex
from ssl import SSLError
import ffmpeg
import shutil


class PlaylistPlaybackManager(object):
    
    def __init__(self, url, output_folder, file_type) -> None:
        self.stop = False
        self.playlist = pytube.Playlist(url)
        try:
            client.hail(self.playlist.title)
        except KeyError as e:
            client.warn("Playlist information cannot be accessed", 
                        "Cannot create playback from Private Playlist or Youtube Mix.")
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

class VideoHelper:
    @staticmethod
    def get_title(file_path):
        ic("GET_TITLE:", file_path)
        try:
            return os.path.basename(file_path)
        except Exception as e:
            ic("Error getting title:", e)
            return None

    @staticmethod
    def is_mp4_corrupt(file_path):
        ic("IS_MP4_CORRUPT: Checking if MP4 file is corrupt")
        try:
            ffmpeg.input(file_path).output("null", f="null", loglevel="quiet").run()
        except ffmpeg._run.Error:
            ic("Corrupt file:", file_path)
            return True
        else:
            ic("Non-corrupt file:", file_path)
            return False

    @staticmethod
    def create_playback_from_video(video: pytube.YouTube, output_folder, file_type, retries=10) -> str | None:
        ic("CREATE_PLAYBACK_FROM_VIDEO: Creating playback from video")
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            ic("Output folder:", output_folder)

            folder = os.path.join(output_folder, video.video_id) + "\\"
            ic("Folder:", folder)

            if os.path.exists(folder):
                ic("Fetching from files...")
                file_path = os.path.join(folder, os.listdir(folder)[0])
            else:
                ic("Fetching from servers...")
                file_ext = None if file_type == "any" else file_type
                stream = ic(video.streams.filter(only_audio=True, file_extension=file_ext).first())
                file_path = stream.download(folder)
                ic("File location:", file_path)

            ic("Download completed")
            
            if VideoHelper.is_mp4_corrupt(file_path):
                if retries > 0:
                    ic(f"'{file_path}' is corrupted. Retrying download...")
                    shutil.rmtree(file_path)
                    return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
                else:
                    ic(f"'{file_path}' cannot be downloaded after {retries} retries. Skipping...")
            else:
                ic(f"Successfully acquired '{video.title}'")
                return file_path

        except AgeRestrictedError as e:
            ic(f"'{video.title}' is age restricted and requires login. ID: {video.video_id}")

        except SSLError as e:
            if retries > 0:
                ic(f"Network error downloading '{video.title}'. Retrying...")
                time.sleep(0.1)
                return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
            else:
                ic(f"Network error downloading '{video.title}' after {retries} retries. Skipping...")

        except Exception as e:
            ic("Error creating playback from video:", e)

        return None

    @staticmethod
    def create_playback(url, output_folder, file_type) -> str | None:
        ic("CREATE_PLAYBACK: Creating playback from URL")
        return ic(VideoHelper.create_playback_from_video(pytube.YouTube(url), output_folder, file_type))
   

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


class PlaybackManager:    
    
    def __init__(self):
        self.tracks = []
        self.current = -1    
        self.generator = None
        self.volume = int(settings.get("volume"))

    def reset(self = None) -> bool:
        ic("Resetting playback manager")
        if self is not None:
            for track in self.tracks:
                track.player.pause()
                track.player.delete()
            self.tracks.clear()
            self.current = -1
            self.generator = None
        return True


    def play(self, settings) -> bool:
        ic("Starting playback")
        # get url
        import commons
        url = settings.get("url") or settings.get("commons") and commons.storage[settings["commons"]]

        # determine content type
        content_type = ContentType.NONE
        if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url):
            content_type = ContentType.VIDEO
        if re.search(r"list=[0-9A-Za-z_-]+", url):
            content_type = ContentType.PLAYLIST
        ic(content_type)

        if content_type is ContentType.PLAYLIST:
            try:
                playlist = PlaylistPlaybackManager(url, settings["output_folder"], settings["file_type"])
                iterator = playlist.yield_iterate()
                if playlist.has_next():
                    def gen():
                        for track_source in iterator:
                            ic("Yielding new track:", track_source)
                            if track_source is None:
                                continue
                            t = Track(track_source)
                            t.push_handlers(on_end=self.skip)
                            t.player.volume = self.volume / 100
                            self.tracks.append(t)
                            yield t
                    self.generator = gen()
                    t = next(self.generator)
                    self.current = 0 
                    self.get_current().player.play()
                    client.info(VideoHelper.get_title(t.source))
            except Exception as e: 
                ic("Error playing playlist:", e)

        if content_type is ContentType.VIDEO:
            try:                    
                t = Track(VideoHelper.create_playback(url, settings["output_folder"], settings["file_type"]))
                self.tracks.append(t)
                t.player.volume = self.volume / 100
                t.push_handlers(on_end=self.skip)
                self.current = 0
                self.get_current().player.play()
                client.info(VideoHelper.get_title(t.source))
            except Exception as e: 
                ic("Error playing video:", e)

        try:
            pyglet.app.run()
        except Exception as e:
            pass

        return True

    def get_current(self) -> Track | None:
        current = self.tracks[self.current] if 0 <= self.current < len(self.tracks) else None
        ic("Current track:", current)
        return current

    def pause(self):
        ic("Pausing playback")
        if self.get_current() is None:
            return
        self.get_current().player.pause()

    def resume(self):
        ic("Resuming playback")
        if self.get_current() is None:
            return
        self.get_current().player.play()

    def prev(self):
        ic("Playing previous track")
        if self.get_current() is None or self.current < 0:
            return
        self.get_current().player.pause()
        self.current -= 1
        self.get_current().player.seek(0)
        self.get_current().player.play()
        client.info(VideoHelper.get_title(self.get_current().source))

    def skip(self):
        ic("Skipping to next track")
        if self.get_current() is None:
            return
        self.get_current().player.pause()
        # If there is no next track, try to generate one 
        if self.current + 1 == len(self.tracks):
            if self.generator is None:
                return
            # New track needs to get generated
            next_track = next(self.generator, None)
            if next_track is None:
                return
        # Assign next track
        self.current += 1
        self.get_current().player.seek(0)
        self.get_current().player.play()
        client.info(VideoHelper.get_title(self.get_current().source))

    def set_volume(self, value) -> bool:
        ic("Setting volume to", value)
        self.volume = value
        for track in self.tracks:
            track.player.volume = value / 100
        return True


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1