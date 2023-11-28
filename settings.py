from icecream import ic

def valuefy(value) -> str:
    return str(value).lower()

# storage["key"] should be avoided
storage = {
    "fail": valuefy(True),
    "warn": valuefy(True),
    "hail": valuefy(True),
    "info": valuefy(True),
    "volume": valuefy("40")
}
invocations = {
    "volume": lambda val, pb: ic(pb.set_volume(int(val)))
}

def get(settings, print_info=False):
    import client

    if type(settings) is dict:
        if "key" not in settings:
            for key in settings.keys():
                value = storage[key]
                if print_info: client.info("Read settings: " + str((key, value)))
        else:
            key = settings["key"]
            value = storage[key]
            client.info("Read settings: " + str((key, value)))
    else:
        value = storage[settings]
    return value


def set(settings, playback):
    import client

    if (len(settings.keys()) > 0 and len(settings.values()) > 0):
        key, value = (next(iter(settings.items()))
                      if "key" not in settings or "value" not in settings 
                      else (settings["key"], settings["value"]))
        
        storage[key] = valuefy(value)
        if (key in invocations): 
            invocations[key](value, playback)
        client.info("Write settings: " + str((key, value)))