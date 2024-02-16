import logging
import enum 
import re
import os


logger = logging.getLogger(f"root___.weevil_.settngs")
logger.info(f"Logging to file enabled.")


# Inheritance in python sucks, using an enum instead
class ValueType (enum.Enum):
    Dict = 0
    Boolean = 1
    PercentInteger = 2
    String = 3
    Integer = 4
    Float = 5
    Path = 6
    AudioFile = 7

    def is_valid(type, value) -> bool:

        if type is ValueType.PercentInteger:
            if (re.search(r"\D", value) is not None):
                return False
            if (int(value) < 0 or int(value) > 100):
                return False

        if type is ValueType.Boolean:
            if (StorageItem.valuefy(value) != "false" and
                StorageItem.valuefy(value) != "true"):
                return False
            
        if type is ValueType.String:
            pass

        if type is ValueType.Integer:
            if (re.search(r"\D", value) is not None):
                return False

        if type is ValueType.Dict:
            pass

        if type is ValueType.Float:
            try:
                float(value)
            except ValueError:
                return False

        if type is ValueType.Path:
            if not os.path.isdir(value):
                return False

        if type is ValueType.AudioFile:
            #TODO: figuere out which file types pytube can return
            if not (value == "any" or
                    value == "mp4"):
                return False

        return True


class StorageItem:
    def __init__(self, type: ValueType, value, action = None) -> None:
       self.type = type
       self.value = StorageItem.valuefy(value)
       self.action = action 

    def get_value(self) -> str:
        return self.value

    def set_value(self, value, silent=True) -> bool:
        if ValueType.is_valid(self.type, value):
            self.value = StorageItem.valuefy(value)
            return True
        else:
            if not silent: 
                import client
                client.warn(message=f"Value '{value}' does not fit the requirements for {self.type}!")
            return False

    def get_type(self) -> ValueType:
        return self.type

    def invoke(self, value, playback):
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
    "volume_db": StorageItem(ValueType.Float, 0, lambda val, pb: pb.set_volume(float(val))),
    "no_overflow_mode": StorageItem(ValueType.Integer, 1),
    "output_folder": StorageItem(ValueType.Path, os.getcwd()),
    "preferred_file_type": StorageItem(ValueType.AudioFile, "any")
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
            logger.info("Read settings: " + str((key, value)))
            if print_info: client.info("Read settings: " + str((key, value)))
    else:
        value = storage[settings].get_value()

    return value


def set(settings, playback):
    import client

    if len(settings.keys()) == 0:
        client.warn("No key specified!")
        return

    if len(settings.values()) == 0:
        client.warn("No value specified!")
        return

    key, value = (next(iter(settings.items()))
                  if "key" not in settings or "value" not in settings 
                  else (settings["key"], settings["value"]))
    
    if storage[key].set_value(value, silent=False):
        storage[key].invoke(value, playback)
        logger.info("Write settings: " + str((key, value)))
        

def save_to_files(settings):
    import json
    import client

    folder_location = settings["location"]
    file_path = os.path.join(folder_location, "settings.json")
    
    data_to_save = {}
    for key, storage_item in storage.items():
        data_to_save[key] = {
            "type": storage_item.get_type().name,
            "value": storage_item.get_value(),
        }

    try:
        os.makedirs(folder_location, exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(data_to_save, file)
        logger.info("Settings saved to file: " + file_path)
        client.info("Settings saved to file: " + file_path)
    except Exception as e:
        logger.error("Failed to save settings to file. Error: " + str(e))
        client.fail("Failed to save settings to file. Error: " + str(e))

    return True


def load_from_files(settings):
    import json
    import client

    file_path = os.path.join(settings.get("location"), "settings.json")
    
    if not os.path.exists(file_path):
        logger.warn("The settings file (" + file_path + ") does not exist.")
        client.warn("The settings file (" + file_path + ") does not exist.")
        return

    try:
        with open(file_path, 'r') as file:
            data_loaded = json.load(file)

        for key, data in data_loaded.items():
            value = data["value"]
            storage[key].set_value(value)

        logger.info("Settings loaded from file: " + file_path)
        client.info("Settings loaded from file: " + file_path)
    except Exception as e:
        logger.error("Failed to load settings from file. Error: " + str(e))
        client.fail("Failed to load settings from file. Error: " + str(e))

    return True

