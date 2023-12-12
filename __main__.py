from pytube import YouTube
from playbackMan import VideoPlaybackManager, PlaylistPlaybackManager, PlaybackManager
from mpWrapper import MediaPlayer
from threadPtr import ThreadPtr
from icecream import ic
from os import getcwd
import os
from sys import argv
import threading
import re
from requests import HTTPError
import logging
import client
import settings
import arguments

debug_mode = True if len(argv)>1 and "DEBUG" in argv[1] else False
if not debug_mode: 
    def log_to_file(message, log_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.txt")):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s') #format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        logging.info(message)
    ic.outputFunction = log_to_file


arguments.initiate([
    {
        # Print 'help.txt'
        "names": [ "help", "-h", "--help" ],
        "function": lambda settings: ic(client.printHelp()),
        "flags": [ 

        ]
    },
    {
        # Play a video or playlist
        "names": [ "play" ],
        "function":lambda settings: ic(PlaybackManager.stop(playback)) and ic(playback.play(settings)),
        "flags": [
            { 
                "names": [ "--url", "-u" ],
                "name_settings":"url"
            },
            { 
                "names": [ "--output", "-o" ],
                "name_settings":"output_folder",
                "default":getcwd() + "\\"
            },
            { 
                "names": [ "--fileType", "-f" ], 
                "name_settings":"file_type",
                "default":'any'
            },
        ]
    },
    {
        # Clear the terminal
        "names": [ "clear", "cls" ],
        "function":lambda settings: ic(os.system('cls' if os.name=='nt' else 'clear')),
        "flags": [ 

        ]
    },
    {
        # Pause playback
        "names": [ "pause", "p" ],
        "function":lambda settings: ic(playback.current.pause()),
        "flags": [ 

        ]
    },
    {
        # Resume playback
        "names": [ "resume", "r" ],
        "function":lambda settings: ic(playback.current.resume()),
        "flags": [

        ]
    },
    {
        # Exit weevil
        "names": [ "exit", "close", "quit" ],
        "function":lambda settings: ic(exit_success()),
        "flags": [

        ]
    },
    {
        # Get a setting
        "names": [ "get"],
        "function": lambda s: ic(settings.get(s, print_info=True)),
        "flags": [
            # dynamic
            {
                "names": [ "--key", "-k" ],
                "name_settings": "key"
            },

            # hardcoded
            {
                "names": [ "--title_declerations", "-t"],
                "name_settings": "hail"
            },   
            {
                "names": [ "--info", "-i"],
                "name_settings": "info"
            },     
            {
                "names": [ "--failures", "-f"],
                "name_settings": "fail"
            },
            {
                "names": [ "--warnings", "-w"],
                "name_settings": "warn"
            },            
            {
                "names": [ "--volume", "-vol"],
                "name_settings": "volume"
            },
        ]
    },
    {
        # Set a settings
        "names": [ "set" ],
        "function": lambda s: ic(settings.set(s, playback.current)), 
        "flags": [
            # dynamic
            {
                "names": [ "--key", "-k" ],
                "name_settings": "key"
            },
            {
                "names": [ "--value", "-v" ],
                "name_settings": "value"
            },

            # hardcoded
            {
                "names": [ "--title_declerations", "-t"],
                "name_settings": "hail"
            },   
            {
                "names": [ "--info", "-i"],
                "name_settings": "info"
            },     
            {
                "names": [ "--failures", "-f"],
                "name_settings": "fail"
            },
            {
                "names": [ "--warnings", "-w"],
                "name_settings": "warn"
            },         
            {
                "names": [ "--volume", "-vol"],
                "name_settings": "volume"
            }
        ]
    },
    {
        # Play next track
        "names": [ "next", "skip", "s" ],
        "function": lambda settings: ic(playback.current.next()),
        "flags": [
        
        ]
    },
    {
        # Play previous track
        "names": [ "previous", "prev" ],
        "function": lambda settings: ic(playback.current.prev()),
        "flags": [
            # TODO
            # {
            #     "names": [ "--count", "-c" ],
            #     "name_settings": "execution_count",
            #     "default": str(1)
            # },
        ]
    },
    {
        # Print a list of all downloaded playlists and their videos
        "names": [ "list_playlists", "lp" ],
        "function": lambda settings: ic(client.list_playlists(settings)),
        "flags": [
            {
                "names": [ "--directory", "-dir" ],
                "name_settings": "directory",
                "default": getcwd()
            },
            {
                "names": [ "--show_id", "-si" ],
                "name_settings": "show_id",
                "default": str(debug_mode)
            }
        ]
    },
])

exit_flag = False
playback = PlaybackManager()

def parse_tokens(input:str, arg_library):
    # get the argument and it's definition
    argument = re.findall(r"\A[a-zA-Z_]+", input)[0]
    arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
    if arg_def is None: 
        raise Exception("Specified argument does not exist!")
    ic(argument)
    ic(input)

    # search for pseudo legal flags and values
    input = '"'+input+'"'
    pattern = r"(?:[^\"]*\"){2}([^\"]*)(?=\")"
    values = re.findall(pattern, input)
    flags = [re.findall(r"(?<=\s)-[a-zA-Z-_]+\b", flag)[0] 
             for flag in re.findall(pattern, '"'+input)
             if len(re.findall(r"(?<=\s)-[a-zA-Z-_]+\b", flag)) > 0]
    ic(values)
    ic(flags)

    # merge the regiesterd flags and their values
    # load defaults
    flag_mapping = {flag_def["name_settings"]: flag_def["default"] 
                    for flag_def in arg_def["flags"] 
                    if "default" in flag_def}
    ic(flag_mapping)

    # make flag entry without value
    flag_mapping.update({flag_def["name_settings"]:""
                         for flag in flags
                         for flag_def in arg_def["flags"]  
                         if flag in flag_def["names"]})
    ic(flag_mapping)

    # override with custom values, if any
    flag_mapping.update({flag_def["name_settings"]: val 
                         for flag, val in zip(flags, values) 
                         for flag_def in arg_def["flags"]  
                         if flag in flag_def["names"]})    
    ic(flag_mapping)


    return arg_def, flag_mapping


def handle_arg(argument, settings):
    ic(threading.Thread(target=argument["function"], args=[settings], daemon=True).start())


def exit_success(): 
    ic("EXit success.")
    exit()

def exit_failure(): 
    ic("Exit Failure.")
    exit()   

def exit():
    global exit_flag
    exit_flag = True


if __name__ == "__main__":
    client.info("Type 'help' to retrieve documentation.")
    while exit_flag == False:
        try:
            tokens = ic(input())
            argument, flags = ic(parse_tokens(tokens, arguments.get()))
            ic(handle_arg(argument, flags))
        except  HTTPError as e:
            if debug_mode: 
                raise(e)
            else: 
                client.fail("An HTTP Error occured.")
                ic(e)
                exit_failure()
        except Exception as e:
            if debug_mode: 
                raise(e)
            else: 
                ic(e)
    
    exit_success()