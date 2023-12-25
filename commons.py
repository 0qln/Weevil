

# Store all commonly used urls and their custom name.
storage = { }

def add(key, value):
    storage[key] = value

def remove(key):
    del storage[key]

def manage(settings):
    key = settings["customname"]
    value = settings["url"]

    if ("add" in settings):
        add(key, value)

    if ("remove" in settings):
       remove(key); 

    print (storage)