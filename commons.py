

# Store all commonly used urls and their custom name.
storage = { }


def add(key, value):
    import client
    if key in storage:
        client.warn(f"Custom {str({key: storage[key]})} was overridden!")
    else:
        client.info(f"Custom {str({key: value})} was added.")
    storage[key] = value


def remove(key):
    import client
    if key in storage:
        client.info(f"Removed custom: {str({key: storage[key]})}")
        del storage[key]
    else:
        client.warn(f"Custom {key} was not found!")


def list(settings):
    import client

    client.hail("Commons config")

    # name specified:
    if ("customname" in settings):
        client.info({ settings["customname"]:storage[settings["customname"]] })
        return

    # url specified:    
    if ("url" in settings and settings["url"] != ""):
        reverse_storage = { value: key for key, value in storage.items() }
        client.info({ reverse_storage.get(settings["url"]):settings["url"] })
        return

    # no specific common specified:
    for kvp in storage:
        client.info(str({ kvp: storage[kvp] }))
    

def manage(settings):
    import client

    print(settings)

    if ("list" in settings):
        list(settings)
        return   

    if "customname" not in settings:
        client.warn("No name specified!")
        return

    key = settings["customname"]
    value = settings["url"]
    mode = ("r" if "remove" in settings else 
            "a" if "add" in settings else 
            '-')

    if mode == 'a': add(key, value)
    if mode == 'r': remove(key) 


def save_to_files(settings):
    import json
    import client
    import os

    folder_location = settings["location"]
    file_path = os.path.join(folder_location, "commons.json")   
    global storage 
    data_to_save = storage

    try:
        os.makedirs(folder_location, exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(data_to_save, file)
        client.info("Commons saved to file: " + file_path)
    except Exception as e:
        client.fail("Failed to save commons to file. Error: " + str(e))

    return True



def load_from_files(settings):
    import json
    import client
    import os

    file_path = os.path.join(settings.get("location"), "commons.json")
    
    if not os.path.exists(file_path):
        client.warn("The commons file (" + file_path + ") does not exist.")
        return

    try:
        with open(file_path, 'r') as file:
            data_loaded = json.load(file)

        global storage
        storage = data_loaded

        client.info("Commons loaded from file: " + file_path)
    except Exception as e:
        client.fail("Failed to load commons from file. Error: " + str(e))




