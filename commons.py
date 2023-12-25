

# Store all commonly used urls and their custom name.
storage = { }


def add(key, value):
    storage[key] = value


def remove(key):
    del storage[key]


def manage(settings):
    import client

    key = settings["customname"]
    value = settings["url"]

    if ("add" in settings):
        add(key, value)

    if ("remove" in settings):
       remove(key); 

    client.info("Updated customs: " + str({key: value}))


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




