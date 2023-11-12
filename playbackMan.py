
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
            client.info(self.playlist.title, self.playlist.owner, str(self.playlist.length) + " tracks")
        except KeyError as e:
            client.fail("Playlist information cannot be accessed", 
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
        for media_player in self.yield_iterate():
            if media_player is None: continue
            callback(media_player)
            ic(VideoPlaybackManager.play(media_player))
                

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
            self.current_mp += 1
            yield self.get_current()


    def get_current(self) -> MediaPlayer:
        return self.videos[self.current_mp]


class VideoPlaybackManager:
    def play(media_player:MediaPlayer) -> None:
        client.info(str(media_player.get_content_title()),
                    str(datetime.timedelta(seconds=media_player.get_duration())))
        ic(media_player.play())
        state = MediaPlayerState.PLAYING
        while (state != MediaPlayerState.STOPPED and 
                state != MediaPlayerState.SKIPPING): 
            state = ic(media_player.get_new_state())


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
        

    def create_playback_from_video(video:pytube.YouTube, output_folder, file_type, retrys = 20) -> MediaPlayer | None:
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
                msource = ic(stream.download(file_pat))
            else:
                msource = ic(file_pat + stream.default_filename)

            if VideoPlaybackManager.is_mp4_corrupt(msource):
                client.fail("'" + video.title + " is currupted. Consider deleting the file, so it can be redownloaded.", 
                            "path: " + msource)
            else:
                mp = MediaPlayer()
                ic(mp.load(msource, video.title, video.length))


        except AgeRestrictedError as e:
            client.fail("'" + video.title + "' is age restricted, and can't be accessed without logging in.", 
                        "<ID=" + video.video_id + ">")
        
        except SSLError as e:
            if retrys > 0:
                client.fail("'" + video.title + "' could not be downloaded due to a network error.", 
                            "Retrys left: " + str(retrys), e.strerror)
                time.sleep(0.1)
                mp = ic(VideoPlaybackManager.create_playback_from_video(video, output_folder, file_type, retrys-1))
            else:
                client.fail("'" + video.title + "' could not be downloaded due to a network error.", 
                            "No retrys left.", e.strerror)
            
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