from icecream import ic
import enum, re

# Inheritance in python sucks, using an enum instead
class ValueType (enum.Enum):
    Boolean = 1
    PercentInt = 2

    def is_valid(type, value) -> bool:
        if type is ValueType.PercentInt:
            if (re.search(r"\D", value) is not None):
                return False
            if (int(value) < 0 or int(value) > 100):
                return False

        if type is ValueType.Boolean:
            if (StorageItem.valuefy(value) != "false" and
                StorageItem.valuefy(value) != "true"):
                return False

        return True


class StorageItem:
    def __init__(self, type: ValueType, value, action = None) -> None:
       self.type = type
       self.value = StorageItem.valuefy(value)
       self.action = action 

    def get_value(self) -> str:
        return self.value

    def set_value(self, value) -> bool:
        if (ValueType.is_valid(self.type, value)):
            self.value = StorageItem.valuefy(value)
            return True
        else:
            return False

    def get_type(self) -> ValueType:
        return self.type

    def invoce(self, value, playback):
        if self.action is not None:
            self.action(value, playback)

    def valuefy(value) -> str:
        try:
            return str(value).lower()
        except:
            return ""


# storage["key"] should be avoided
storage = {
    "fail": StorageItem(ValueType.Boolean, True),
    "warn": StorageItem(ValueType.Boolean, True),
    "hail": StorageItem(ValueType.Boolean, True),
    "info": StorageItem(ValueType.Boolean, True),
    "volume": StorageItem(ValueType.PercentInt, 35, lambda val, pb: ic(pb.set_volume(int(val)))),
}


def get(settings, print_info=False):
    import client

    if type(settings) is dict:
        if "key" not in settings:
            for key in settings.keys():
                value = storage[key].get_value()
                if print_info: client.info("Read settings: " + str((key, value)))
        else:
            key = settings["key"]
            value = storage[key].get_value()
            client.info("Read settings: " + str((key, value)))
    else:
        value = storage[settings].get_value()

    return value


def set(settings, playback):
    import client

    if (len(settings.keys()) > 0 and len(settings.values()) > 0):
        key, value = (next(iter(settings.items()))
                      if "key" not in settings or "value" not in settings 
                      else (settings["key"], settings["value"]))
        
        if not storage[key].set_value(value):
            client.warn("There seems to be something wrong with the value: '" + str(value) + "'")
        else:
            storage[key].invoce(value, playback)
            client.info("Write settings: " + str((key, value)))

