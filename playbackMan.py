
from mpWrapper import MediaPlayer, MediaPlayerState
import pytube, os, threading
from icecream import ic
import re
import enum


class PlaylistPlaybackManager(object):
    
    def __init__(self, settings) -> None:
        self.playlist = pytube.Playlist(settings["url"])
        self.videos = [MediaPlayer]
        self.current_mp = 0
        self.preferred_file_type = settings["file_type"]
        
        # Replace invalid characters with underscores in the playlist title
        sanitized_title = re.sub(r'[\\/:*?"<>|]', '_', self.playlist.title)
        self.path = settings["output_folder"] + sanitized_title + "\\"
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def play(self) -> None:
        for m in self.yield_iterate():
            m.play()
            state = MediaPlayerState.PLAYING
            while (state != MediaPlayerState.STOPPED and 
                   state != MediaPlayerState.SKIPPING): 
                state = m.get_new_state()
                ic(state)

                

    def fill(self) -> [MediaPlayer]:
        for video in self.playlist.videos:
            self.videos.append(VideoPlaybackManager.create_playback_from_video(
                video, self.path, self.preferred_file_type))
        return self.videos 


    def yield_iterate(self):
        for video in self.playlist.videos_generator():
            self.videos.append(VideoPlaybackManager.create_playback_from_video(
                video, self.path, self.preferred_file_type))
            self.current_mp += 1
            yield self.get_current()


    def get_current(self) -> MediaPlayer:
        return self.videos[self.current_mp]


class VideoPlaybackManager:
    def create_playback_from_video(video:pytube.YouTube, output_folder, file_type) -> MediaPlayer:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # aquire data
        streams = video.streams
        msource = os.path.join(output_folder, (video.title)) #+file_type
        if not os.path.exists(msource):
            stream = (video.streams
                    .filter(only_audio=True) #, file_extension=file_type
                    .first())
            msource = stream.download(output_folder)     
        ic(msource)

        # create mediaplayer
        mp = MediaPlayer()
        mp.load(msource)

        return mp

    def create_playback(settings) -> MediaPlayer:
        mp = VideoPlaybackManager.create_playback_from_video(
            pytube.YouTube(settings["url"]), 
            settings["output_folder"],
            settings["file_type"])

        return mp
    

class PlaybackManager:    
    def __init__(self):
        self.current = MediaPlayer()
        self.content_type = ContentType.NONE
    
    def play(self, settings):
        # determine content type
        

        #self.content_type = ContentType.NONE
        ic(self.content_type)


class ContentType(enum.Enum):
    NONE = -1
    PLAYLIST = 0
    VIDEO = 1