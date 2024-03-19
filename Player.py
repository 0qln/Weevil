import Track 
import VideoHelper
import settings
from typing import Type as T
import pytube
import re
import logging
import client
from abc import ABC, abstractmethod
from eventdisp import Event, EventDispatcher



class Player: 
    ...

class Player(ABC, EventDispatcher):

    def __init__(self, item_type, source_to_item, logger: logging.Logger, silent=[False], do_load=[True]) -> None:
        super().__init__()
        self.silent = silent 
        self.logger = logger
        self.do_load = do_load
        self.item_storage = []
        self.item_sources = []
        self.current = 0
        self.item_type = item_type
        self.converter = source_to_item
        def generate():
            for source in self.item_sources:
                newItem = self.converter(source)
                if newItem:
                    self.item_storage.append(newItem)
                    self.logger.info(f"Yield new item from source: {newItem=}")
                    yield True
            self.logger.info(f"Item generator exhausted.")
            yield False

        self.item_generator = generate()


    def clear(self) -> None:
        self.item_sources.clear()
        self.item_storage.clear()
        self.current = 0


    def load_source(self, source) -> bool:
        self.logger.info(f"Load {source=}")
        self.item_sources.append(source)
        return True


    def get_curr(self) -> Player|None:
        current:Player|None = (self.item_storage[self.current] if self.current > -1 and self.current < len(self.item_storage) else None)
        self.logger.info(f"{current=}")
        return current


    '''
    Returns: Wether the initialization was a success. 
    '''
    def init_next(self) -> bool:
        self.logger.info("Init next begin")
        result:bool = next(self.item_generator)
        item:Player|None = self.get_curr()
        if result == True: 
            result = item.init_next()
        self.logger.info(f"Init next {result=}")
        return result

   
    def set_silent(self, value:bool) -> None: self.silent[0] = value
    def set_load(self, value:bool) -> None: self.do_load[0] = value


    def count_items(self) -> dict:
        result = {}
        # Add count for the class if it already exists in the result dictionary
        if self.__class__ in result:
            result[self.__class__] += 1
        else:
            result[self.__class__] = 1

        # Iterate over item_storage and update counts recursively
        for player in self.item_storage:
            for class_key, count in player.count_items().items():
                # Add count for each class encountered
                if class_key in result:
                    result[class_key] += count
                else:
                    result[class_key] = count

        return result


    def stop_curr(self) -> None:
        item:Player|None = self.get_curr()
        self.logger.info(f"stop {item=}")
        if item is not None: item.stop_curr()


    def start_curr(self) -> None:
        item:Player|None = self.get_curr()
        self.logger.info(f"start {item=}")
        if item is not None: item.start_curr()


    def pause_curr(self) -> None:
        item:Player|None = self.get_curr()
        self.logger.info(f"pause {item=}")
        if item is not None: item.pause_curr()


    def resume_curr(self) -> None:
        item:Player|None = self.get_curr()
        self.logger.info(f"resume {item=}")
        if item is not None: item.resume_curr()


    def peek_decr(self) -> bool:
        self.logger.info(f"Peek decr {self.get_curr()=}")
        assert self.get_curr() is not None
        if self.current - 1 < 0: return False
        self.current -= 1
        return True


    def peek_incr(self) -> bool:
        self.logger.info(f"Peek incr {self.get_curr()=}")
        assert self.get_curr() is not None
        if self.current + 1 >= len(self.item_storage): return False
        self.current += 1
        return True 
    

    def set_volume(self, value) -> bool:
        item:Player|None = self.get_curr()
        self.logger.info(f"set vol {item=}")
        if item is not None: item.set_volume(value)


    def has_curr(self):
        return self.get_curr() is not None and self.get_curr().has_curr()


    '''
    Returns: Wether a skip has been made
    '''
    def skip(self) -> bool:
        self.logger.info(f"skip {self.get_curr()=}")

        if self.get_curr().skip(): 
            # A child has skipped succesfully, return true
            self.logger.info(f"skip RET: child +")
            return True

        self.stop_curr() 

        if self.peek_incr():
            self.logger.info(f"skip RET: old -")
            self.start_curr()
            self.logger.info(f"skip RET: old +")
            return True

        # Try generating a new item, if needed
        self.logger.info(f"{next(self.item_generator)=}")

        if self.peek_incr():
            self.logger.info(f"skip RET: new -")
            while not self.get_curr().init_next():
                self.logger.info(f"{next(self.item_generator)=}")
                if not self.peek_incr():
                    self.logger.info(f"skip RET: new none +")
                    return False
            self.start_curr()
            self.logger.info(f"skip RET: new +")
            return True

        # No new item could be generated, return false
        self.logger.info(f"skip RET: none +")
        return False



    '''
    Returns: Wether a prev has been made
    '''
    def prev(self) -> bool:
        self.logger.info(f"prev {self.get_curr()=}")

        if self.get_curr().prev():
            # A child has preved succesfully, return true
            return True
        
        # Pause current track and decrease index
        self.stop_curr()

        if self.peek_decr():
            self.start_curr()
            return True

        return False


    def dispatch_end(self):
        self.logger.info(f"Dispatch end of {self=}")
        self.dispatch(Event(name="player.end", data={"player":self}))


    def fetch_all(self) -> None:
        self.logger.info(f"Playback manager: fetch all")
        while self.do_load[0] and next(self.item_generator):
            self.item_storage[-1].fetch_all()
        interrupted = not self.do_load[0]
        self.logger.info(f"Playback manager: Finish fetching all ({interrupted=})")




class TrackPlayer(Player):

    @staticmethod
    def is_source(url:str) -> bool:
        return bool(re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url))


    def __init__(self, url, silent=[False], do_load=[True]) -> None:
        self.info = pytube.YouTube(url)
        self.url = url
        super().__init__(
            Track.Track, 
            lambda video_url: self.create_track(video_url),
            logging.getLogger(f"root___.weevil_.t_playr"),
            silent,
            do_load)
        if not self.silent[0]: client.hail(name="Loading Track", message=self.info.title)
        self.load_source(url)
        self.logger.info("Initiated")


    def create_track(self, url) -> Track.Track:
        self.logger.info(f"create track {url=}")
        track_source, video = VideoHelper.VideoHelper.create_playback(
            url, settings.get("output_folder"), settings.get("preferred_file_type"), self.silent[0]) 
        if track_source is None: 
            return None
        track = Track.Track(track_source, dB=float(settings.get("volume_db")))
        track.register("track.end", lambda e: self.dispatch_end())
        return track


    def has_curr(self):
        return self.get_curr() is not None

    def count_items(self) -> dict:
        result = { self.__class__: 1 }
        return result


    def init_next(self) -> bool:
        result:bool = next(self.item_generator)
        self.logger.info(f"Init next track {result=}")
        return result


    def peek_incr(self) -> bool: 
        return False


    def peek_decr(self) -> bool:
        return False


    def skip(self) -> bool:
        self.logger.info("Skip track")
        return False


    def prev(self) -> bool:
        self.logger.info("Previous track")
        return False


    def stop_curr(self) -> None:
        item:Track.Track|None = self.get_curr()
        self.logger.info(f"stop {item=}")
        if item is None or item.is_disposed(): return
        item.dispose()


    def start_curr(self) -> None:
        item:Track.Track|None = self.get_curr()
        self.logger.info(f"start {item=}")
        if item is None: return
        if not self.silent[0]: client.hail(name="Playing Track", message=self.info.title)
        item.initiate()
        item.play()


    def pause_curr(self) -> None:
        item:Track.Track|None = self.get_curr()
        self.logger.info(f"pause {item=}")
        if item is not None: item.pause()


    def resume_curr(self) -> None:
        item:Track.Track|None = self.get_curr()
        self.logger.info(f"resume {item=}")
        if item is not None: item.play()


    def set_volume(self, value) -> bool:
        item:Track.Track|None = self.get_curr()
        self.logger.info(f"set vol {item=}")
        if item is not None: item.set_volume(value)


    def fetch_all(self) -> None:
        self.logger.info(f"fetch")
        while self.do_load[0] and next(self.item_generator):
            pass



class PlaylistPlayer(Player):

    @staticmethod
    def is_source(url:str) -> bool:
        return bool(re.search(r"list=[0-9A-Za-z_-]+", url))


    def initializer(self, track_url) -> TrackPlayer:
        t = TrackPlayer(track_url, self.silent, self.do_load)
        t.register("player.end", lambda e: self.skip() or self.dispatch_end())
        return t


    def __init__(self, url, silent=[False], do_load=[True]) -> None:
        self.info = pytube.Playlist(url)
        
        super().__init__(
            TrackPlayer,
            self.initializer,
            logging.getLogger(f"root___.weevil_.p_playr"),
            silent,
            do_load)
        if not self.silent[0]: client.hail(name="Playlist", message=self.info.title)
        [self.load_source(source) for source in self.info.url_generator()]
        self.logger.info(f"Initiated {url=}")
    


class ChannelPlayer(Player):

    @staticmethod
    def is_source(url:str) -> bool:
        return ( 
            # URL
            bool(re.search(r"youtube.com/channel/[a-zA-Z-_0-9]{24}", url))
            # Vanity URL
            # Pytube does not support vanity urls
            # bool(re.search(r"youtube.com/@.*"))
        )


    def initializer(self, playlist_url) -> PlaylistPlayer:
        p = PlaylistPlayer(playlist_url, self.silent, self.do_load)
        p.register("player.end", lambda e: self.skip() or self.dispatch_end())
        return p


    def __init__(self, url, silent=[False], do_load=[True]) -> None:
        self.info = pytube.Channel(url)
        playlistsIDs = set([p.group() for p in re.finditer(
            r"(?<=\"playlistId\":\")[0-9A-Za-z_-]*(?=\")", 
            self.info.playlists_html)])
        
        super().__init__(
            PlaylistPlayer, 
            self.initializer,
            logging.getLogger(f"root___.weevil_.c_playr"),
            silent,
            do_load)
        if not self.silent[0]: client.hail(name="Channel", message=self.info.channel_name)
        [self.load_source("https://www.youtube.com/playlist?list="+id) for id in playlistsIDs]
        self.logger.info(f"Initiated {url=}")



class PlaybackManager(Player):
    
    def initializer(self, url) -> Player|None:
        player = (
                ChannelPlayer(url, self.silent, self.do_load) if ChannelPlayer.is_source(url) else
                PlaylistPlayer(url, self.silent, self.do_load) if PlaylistPlayer.is_source(url) else
                TrackPlayer(url, self.silent, self.do_load) if TrackPlayer.is_source(url) else
                None)
        if player is None:
            client.warn(f"'{url=}' cannot be deciphered or is unsupported (e.g. Vanity URLs).")
            return None

        player.register("player.end", lambda e: self.skip() or self.dispatch_end())
        return player


    def __init__(self) -> None:
        super().__init__(
            Player,
            self.initializer,  
            logging.getLogger(f"root___.weevil_.pbman__")
        )
        self.logger.info(f"Initiated")



