
from mpWrapper import MediaPlayer, MediaPlayerState
import pytube, os, threading, re, enum, time, datetime
from icecream import ic
import settings, client
from pytube.exceptions import AgeRestrictedError
import pytube.exceptions as pyex
from ssl import SSLError
import ffmpeg

class PlaylistPlaybackManager(object):
    
    def __init__(self, url, output_folder, file_type) -> None:
        self.playlist = pytube.Playlist(url)
        try:
            # client.info(self.playlist.title, self.playlist.owner, str(self.playlist.length) + " tracks")
            client.hail(self.playlist.title)
        except KeyError as e:
            client.warn("Playlist information cannot be accessed", 
                        "Cannot create playback from Private Playlist or Youtube Mix.")
            raise e

        self.videos = [MediaPlayer]
        self.current_mp = 0
        self.preferred_file_type = file_type
        
        # Replace invalid characters with underscores in the playlist title
        sanitized_title = re.sub(r'[\\/:*?"<>|]', '_', self.playlist.title)
        self.path = output_folder + self.playlist.playlist_id + "\\" + sanitized_title + "\\"
        if not os.path.exists(self.path): os.makedirs(self.path)

        ic ("PlaylistPlaybackManager initiated successfully.")


    def play(self, callback) -> None:
        iterator = self.yield_iterate()
        current_media_player = next(iterator, None)

        while current_media_player is not None:
            callback(current_media_player)
            
            state = ic(VideoPlaybackManager.play(current_media_player))

            if state == MediaPlayerState.ROLL_BACK:
                current_media_player = self.get_prev()
            else: 
                current_media_player = next(iterator, None) 


    def fill(self) -> [MediaPlayer]:
        for video in self.playlist.videos:
            ic(self.videos.append(VideoPlaybackManager.create_playback_from_video(
                video, self.path, self.preferred_file_type)))
        return self.videos 


    def yield_iterate(self):
        for video in self.playlist.videos_generator():
            ic("Generate Video: ")
            ic(self.videos.append(VideoPlaybackManager.create_playback_from_video(
                video, self.path, self.preferred_file_type)))
            yield self.get_next()

    def get_prev(self) -> MediaPlayer | None:
        if self.current_mp > 0:
            self.current_mp -= 1
            return self.get_current()
        return None
    
    def get_next(self) -> MediaPlayer | None:
        if self.current_mp < len(self.videos):
            self.current_mp += 1
            return self.get_current()
        return None

    def get_current(self) -> MediaPlayer | None:
        return self.videos[self.current_mp] if self.current_mp > 0 and self.current_mp < len(self.videos) else None
    

class VideoPlaybackManager:
    # returns the last known state
    def play(media_player:MediaPlayer) -> MediaPlayerState:
        client.info(str(media_player.get_content_title()))
        ic(media_player.play())
        state = MediaPlayerState.PLAYING
        while (state != MediaPlayerState.STOPPED and
               state != MediaPlayerState.ROLL_BACK and 
               state != MediaPlayerState.SKIPPING): 
            state = ic(media_player.get_new_state())
        return state

    def is_mp4_corrupt(file_path):
        try:
            (
                ffmpeg
                .input(file_path)
                .output("null", f="null", loglevel="quiet")
                .run()
            )
        except ffmpeg._run.Error:
            return True
        else:
            return False
        

    def create_playback_from_video(video:pytube.YouTube, output_folder, file_type, retrys = 10) -> MediaPlayer | None:
        # output folder    
        if not os.path.exists(output_folder): os.makedirs(output_folder)

        # aquire data
        mp = None
        file_ext = None if file_type == "any" else file_type
        file_pat = os.path.join(output_folder, video.video_id) + "\\"
        ic (os.path.exists(file_pat))
        try:
            stream = ic(video.streams.filter(only_audio=True, file_extension=file_ext).first())
            if os.path.exists(file_pat) is False:
                ic(f"Download '{video.title}'...") # Print nothing on success.
                msource = ic(stream.download(file_pat))
            else: 
                ic(f"Get '{video.title}' from files...") # Print nothing on success.
                msource = ic(file_pat + stream.default_filename)

            if VideoPlaybackManager.is_mp4_corrupt(msource):
                # File is corrupted
                if retrys > 0:
                    # Delete and try to download again
                    client.warn(f"'{msource}' is corrupted. Weevil will try to delete and redownload the track.", 
                                f"Retrys left: {str(retrys)}")
                    os.rmdir(file_pat)
                    mp = ic(VideoPlaybackManager.create_playback_from_video(video, output_folder, file_type, retrys-1))
                else:
                    # Unable to fetch file
                    client.fail(f"'{video.title}' cannot be safely downloaded.", "No retrys left.", 
                                f"'{video.title}' will be skipped.")
            else:
                ic(f"'{video.title}' aquired.") # Print nothing on success.
                mp = MediaPlayer()
                mp.load(msource, video.title, video.length)

        # Video is age restriced
        except AgeRestrictedError as e:
            client.warn(f"'{video.title}' is age restricted, and can't be accessed without logging in.", 
                        f"<ID{video.video_id}>")
        
        # Internal SSLError from pytube. Most at the time it's a network error
        except SSLError as e:
            if retrys > 0:
                client.fail(f"'{video.title}' could not be downloaded due to a network error.", 
                            f"Retrys left: {str(retrys)}")
                time.sleep(0.1)
                mp = ic(VideoPlaybackManager.create_playback_from_video(video, output_folder, file_type, retrys-1))
            else:
                client.fail(f"'{video.title}' could not be downloaded due to a network error.", "No retrys left.", 
                            f"'{video.title}' will be skipped.")
            
        return mp
    

    def create_playback(url, output_folder, file_type) -> MediaPlayer | None:
        return ic(VideoPlaybackManager.create_playback_from_video(
            pytube.YouTube(url), output_folder, file_type))
    

class PlaybackManager:    
    def __init__(self):
        self.current = MediaPlayer()
        self.content_type = ContentType.NONE
    
    def play(self, settings):
        # determine content type
        self.content_type = ContentType.NONE
        if re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", settings['url']) is not None:
            self.content_type=ContentType.VIDEO
        if re.search(r"list=[0-9A-Za-z_-]+", settings['url']) is not None:
            self.content_type=ContentType.PLAYLIST
        ic (self.content_type)

        def callback(mp): 
            self.current = mp
            ic ("Update mp: ")
            ic (self.current)

        if self.content_type is ContentType.PLAYLIST:
            try:
                playback = PlaylistPlaybackManager(
                    settings["url"], settings["output_folder"], settings["file_type"])
                playback.play(callback)
            except: 
                return

        if self.content_type is ContentType.VIDEO:
            try:                    
                playback = VideoPlaybackManager.create_playback(
                    settings["url"], settings["output_folder"], settings["file_type"])
                if playback is not None:
                    self.current = playback
                    VideoPlaybackManager.play(playback)
            except: 
                return


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1