

INITIATED = False
ARG_LIBRARY = { }

def initiate(value):
    global INITIATED
    if INITIATED == False:
        global ARG_LIBRARY
        ARG_LIBRARY = value
        INITIATED = True

def get(): 
    return ARG_LIBRARY