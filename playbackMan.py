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
            # client.info(self.playlist.title, self.playlist.owner, str(self.playlist.length) + " tracks")
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
        if not os.path.exists(self.path): os.makedirs(self.path)

        ic ("PlaylistPlaybackManager initiated successfully.")

    def fill(self) -> [str]:
        for video in self.playlist.videos_generator():
            ic("Generate Video: ")
            ic(self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type)))
        return self.videos 


    def yield_iterate(self):
        for video in self.playlist.videos_generator():
            ic("Generate Video: ")
            ic(self.videos.append(VideoHelper.create_playback_from_video(video, self.path, self.preferred_file_type)))
            yield ic(self.get_next())

    def get_prev(self) -> str | None:
        if self.current_mp > 0:
            self.current_mp -= 1
            return self.get_current()
        return None
    
    def get_next(self) -> str | None:
        if self.current_mp < self.playlist.length:
            self.current_mp += 1
            return self.get_current()
        return None

    def has_next(self) -> bool:
        return self.current_mp < self.playlist.length - 1

    def get_current(self) -> str | None:
        return self.videos[self.current_mp] if self.current_mp > 0 and self.current_mp < self.playlist.length else None
    

class VideoHelper:
    def get_title(file_path):
        ic("get_title of ``: "+file_path)
        try:
            return os.path.basename(file_path)

            #METADATA:
                # probe = ffmpeg.probe(file_path)
                # tags = probe.get('format', {}).get('tags', {})
                # return ic(tags.get('title'))
        except Exception as e:
            ic(e)
            return None

    def is_mp4_corrupt(file_path):
        try:
            (
                ffmpeg
                .input(file_path)
                .output("null", f="null", loglevel="quiet")
                .run()
            )
        except ffmpeg._run.Error:
            ic("Corrupt file: " + file_path)
            return True
        else:
            ic("Non Corrupt file: " + file_path)

            # pyglet.media.have_de

            return False
        

    def create_playback_from_video(video:pytube.YouTube, output_folder, file_type, retrys = 10) -> str | None:
        # output folder    
        if not os.path.exists(output_folder): os.makedirs(output_folder)
        ic(output_folder)

        # aquire data
        ret = None
        try:
            folder = os.path.join(output_folder, video.video_id) + "\\"
            ic(folder)
            if os.path.exists(folder):
                ic("Fetching from files...")
                file_pat = os.path.join(folder, os.listdir(folder)[0])
            else: 
                ic("Fetching from servers...")
                file_ext = None if file_type == "any" else file_type
                stream = ic(video.streams.filter(only_audio=True, file_extension=file_ext).first())
                file_pat = stream.download(folder)
                #TODO: store stream info for later usage?
                ic(f"File location: '{file_pat}'")
            ic("Done")

            if VideoHelper.is_mp4_corrupt(file_pat):
                # File is corrupted
                if retrys > 0:
                    # Delete and try to download again
                    client.warn(f"'{file_pat}' is corrupted. Weevil will try to delete and redownload the track. " + f"Retrys left: {str(retrys)}")
                    shutil.rmtree(file_pat)
                    ret = ic(VideoHelper.create_playback_from_video(video, output_folder, file_type, retrys-1))
                else:
                    # Unable to fetch file
                    client.fail(f"'{video.title}' cannot be safely downloaded. " + "No retrys left. " + f"'{video.title}' will be skipped.")
            else:
                ic(f"'{video.title}' aquired.") # Print nothing on success.
                ret = file_pat

        # Video is age restriced
        except AgeRestrictedError as e:
            client.warn(f"'{video.title}' is age restricted, and can't be accessed without logging in. " + f"<ID:{video.video_id}>")
        
        # Internal SSLError from pytube. Most at the time it's a network error
        except SSLError as e:
            if retrys > 0:
                client.fail(f"'{video.title}' could not be downloaded due to a network error. "+ f"Retrys left: {str(retrys)}")
                time.sleep(0.1)
                ret = ic(VideoHelper.create_playback_from_video(video, output_folder, file_type, retrys-1))
            else:
                client.fail(f"'{video.title}' could not be downloaded due to a network error. "+ "No retrys left. " + f"'{video.title}' will be skipped.")
            
        return ret

    def create_playback(url, output_folder, file_type) -> str | None:
        return ic(VideoHelper.create_playback_from_video(pytube.YouTube(url), output_folder, file_type))
    

class EndEvent:
    def __init__(self, track):
        self.track = track

class Track(EventDispatcher):
    def __init__(self, source:str=None) -> None:
        super().__init__()
        self.source = source
        self.player = pyglet.media.Player()
        if (source is not None):
            self.player.queue(pyglet.media.load(source))
            self.player.push_handlers(on_eos=self.dispatch_end)

    def dispatch_end(self):
        (ic("DISPATCH END"))
        self.dispatch_event('on_end')

    def end(self) -> bool:
        (ic("SKIP TO END"))
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
        if (self is not None):
            for track in self.tracks:
                track.player.pause()
                track.player.delete()
            self.tracks.clear()
            self.current = -1
            self.generator = None
        return True


    def play(self, settings) -> bool:
        # get url
        if ("url" in settings):
            url = settings["url"]
        elif ("commons" in settings):
            import commons
            url =  commons.storage[settings["commons"]]

        # determine content type
        self.content_type = ContentType.NONE
        if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url) is not None:
            self.content_type=ContentType.VIDEO
        if re.search(r"list=[0-9A-Za-z_-]+", url) is not None:
            self.content_type=ContentType.PLAYLIST
        ic (self.content_type)


        if self.content_type is ContentType.PLAYLIST:
            try:
                playlist = PlaylistPlaybackManager(url, settings["output_folder"], settings["file_type"])
                iterator = playlist.yield_iterate()
                if (playlist.has_next()):
                    def gen():
                        for track_source in iterator:
                            (ic("YIELD NEW: "+track_source))
                            if (track_source is None): continue
                            t = Track(track_source)
                            t.push_handlers(on_end=self.skip)
                            t.player.volume = self.volume / 100
                            yield t
                    self.generator = gen()
                    t = next(self.generator)
                    self.tracks.append(t)
                    t.push_handlers(on_end=self.skip)
                    t.player.volume = self.volume / 100
                    self.current = 0 
                    self.get_current().player.play()
                    client.info(VideoHelper.get_title(t.source))
            except Exception as e: 
                ic(e)

        if self.content_type is ContentType.VIDEO:
            try:                    
                t = Track(VideoHelper.create_playback(url, settings["output_folder"], settings["file_type"]))
                self.tracks.append(t)
                t.player.volume = self.volume / 100
                t.push_handlers(on_end=self.skip)
                self.current = 0
                self.get_current().player.play()
                client.info(VideoHelper.get_title(t.source))
            except Exception as e: 
                ic(e)

        # Start pyglet
        try:
            pyglet.app.run()
        except:
            pass

        return True

    def get_current(self) -> Track | None:
        if (self.current < 0 or self.current >= len(self.tracks)):
            return None
        return self.tracks[self.current];

    def pause(self):
        if (self.get_current() is None):
            return
        self.get_current().player.pause()

    def resume(self):
        if (self.get_current() is None):
            return
        self.get_current().player.play()

    def prev(self):
        (ic("PREV"))
        if (self.get_current() is None):
            return
        if (self.current < 0):
            return
        self.get_current().player.pause()
        self.current -= 1
        self.get_current().player.seek(0)
        self.get_current().player.play()
        client.info(VideoHelper.get_title(self.get_current().source))

    def skip(self):
        (ic("SKIP"))
        if (self.get_current() is None):
            return
        self.get_current().player.pause()
        # If there is no next track, try to generate one 
        if (self.current + 1 == len(self.tracks)):
            if (self.generator is None):
                # No new track can be generated and none are cached
                return

            # New track needs to get generated
            next_track = next(self.generator, None)
            if (next_track is None):
                # There is no next track and none are cached
                return
            # Append new track
            self.tracks.append(next_track)
        # Assign next track
        self.current += 1
        # Start playback of new track
        self.get_current().player.seek(0)
        self.get_current().player.play()
        client.info(VideoHelper.get_title(self.get_current().source))

    def set_volume(self, value) -> bool:
        self.volume = value
        for track in self.tracks:
            track.player.volume = value / 100
        return True




class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1