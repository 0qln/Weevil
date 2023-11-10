
from mpWrapper import MediaPlayer, MediaPlayerState
import pytube, os, threading, re, enum, time, datetime
from icecream import ic
import settings, client
from pytube.exceptions import AgeRestrictedError


class PlaylistPlaybackManager(object):
    
    def __init__(self, url, output_folder, file_type) -> None:
        self.playlist = pytube.Playlist(url)
        self.videos = [MediaPlayer]
        self.current_mp = 0
        self.preferred_file_type = file_type
        
        # Replace invalid characters with underscores in the playlist title
        ic(self.playlist.title)
        sanitized_title = re.sub(r'[\\/:*?"<>|]', '_', self.playlist.title)
        self.path = output_folder + self.playlist.playlist_id + "\\" + sanitized_title + "\\"
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)

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


    def create_playback_from_video(video:pytube.YouTube, output_folder, file_type) -> MediaPlayer | None:
        # output folder    
        if not os.path.exists(output_folder): os.makedirs(output_folder)

        # aquire data
        file_ext = None if file_type == "any" else file_type
        file_pat = os.path.join(output_folder, video.video_id) + "\\"
        ic (os.path.exists(file_pat))
        try:
            stream = ic(video.streams.filter(only_audio=True, file_extension=file_ext).first())
        except AgeRestrictedError as e:
            client.fail("'" + video.title + "' is age restricted, and can't be accessed without logging in.", 
                        "<ID=" + video.video_id + ">")
            return None
        
        msource = (
            ic(stream.download(file_pat))
        ) if os.path.exists(file_pat) is False else (
            ic(file_pat + stream.default_filename)
        )

        # create mediaplayer
        mp = MediaPlayer()
        ic(mp.load(msource, video.title, video.length))

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
            playback = PlaylistPlaybackManager(
                settings["url"], settings["output_folder"], settings["file_type"])
            playback.play(callback)

        if self.content_type is ContentType.VIDEO:
            playback = VideoPlaybackManager.create_playback(
                settings["url"], settings["output_folder"], settings["file_type"])
            if playback is not None:
                self.current = playback
                VideoPlaybackManager.play(playback)


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1