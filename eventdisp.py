import logging

logger = logging.getLogger('root___.weevil_.eventdp')
logger.info("Logging to file enabled.")

class EventDispatcher:

    def __init__(self):
        self._funcs = {}


    def register(self, event_name, func):
        logger.info(f"Register {event_name = }, {func = } for { self = }")

        if event_name not in self._funcs: 
            self._funcs[event_name] = []

        self._funcs[event_name].append(func)


    def dispatch(self, event):
        logger.info(f"Dispatch {event.name = }, {event.data = } for { self = }")

        if event.name not in self._funcs: 
            return

        for func in self._funcs[event.name]:
            logger.info(f"Dispatch {func = }")
            func(event)


class Event:
    def __init__(self, name, data):
        self.name = name
        self.data = data

