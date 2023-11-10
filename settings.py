from icecream import ic


def valuefy(value) -> str:
    return str(value).lower()

storage = {
    "warn": valuefy(True),
    "info": valuefy(True),
    "volume": valuefy(100)
}

def get(key):
    return storage[key]

# untested
def set(settings):
    if (len(settings.keys()) > 0 and len(settings.values()) > 0):
        key, value = (next(iter(settings.items()))
                      if "key" not in settings or "value" not in settings 
                      else (settings["key"], settings["value"]))
        
        ic ("Change settings: ")
        ic (key, value)
        
        storage[key] = valuefy(value)