from abc import ABC, abstractmethod


class IPlaybackManager(ABC):
 
    @abstractmethod
    def pause(self, settings):
        pass

    @abstractmethod
    def resume(self, settings):
        pass

    @abstractmethod
    def play(self, settings):
        pass

    @abstractmethod
    def skip(self, settings):
        pass

    @abstractmethod
    def prev(self, settings):
        pass



