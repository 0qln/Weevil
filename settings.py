from icecream import ic
import client

def valuefy(value) -> str:
    return str(value).lower()

# storage["key"] should be avoided
storage = {
    "fail": valuefy(True),
    "warn": valuefy(True),
    "hail": valuefy(True),
    "info": valuefy(True),
    "volume": valuefy(100)
}

def get(settings, print_info=False):
    print("1")
    if type(settings) is dict:
        print("2")
        if "key" not in settings:
            print("3")
            print(settings.keys())
            for key in settings.keys():
                print("4")
                print(key)
                value = storage[key]
                if print_info: client.info("Read settings: " + str((key, value)))
        else:
            key = settings["key"]
            value = storage[key]
            client.info("Read settings: " + str((key, value)))
    else:
        value = storage[settings]
    return value

# untested
def set(settings):
    if (len(settings.keys()) > 0 and len(settings.values()) > 0):
        key, value = (next(iter(settings.items()))
                      if "key" not in settings or "value" not in settings 
                      else (settings["key"], settings["value"]))
        
        storage[key] = valuefy(value)
        client.info("Write settings: " + str((key, value)))