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
from client import list_playlists, printHelp, warn, info
import settings
import arguments

debug_mode = True if len(argv)>1 and "DEBUG" in argv[1] else False
if not debug_mode: 
    def log_to_file(message, log_file=os.path.join(getcwd(), "log.txt")):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s') #format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        logging.info(message)
    ic.outputFunction = log_to_file


arguments.initiate([
    {
        "names": [ "help", "-h", "--help" ],
        "function": lambda settings: ic(printHelp()),
        "flags": [ 

        ]
    },
    {
        "names": [ "play" ],
        "function":lambda settings: ic(playback.play(settings)),
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
        "names": [ "pause", "p" ],
        "function":lambda settings: ic(playback.current.pause()),
        "flags": [ 

        ]
    },
    {
        "names": [ "resume", "r" ],
        "function":lambda settings: ic(playback.current.resume()),
        "flags": [

        ]
    },
    {
        "names": [ "exit", "close", "quit" ],
        "function":lambda settings: ic(exit_success()),
        "flags": [

        ]
    },
    {
        "names": [ "set" ],
        "function": lambda s: settings.set(s), 
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
                "names": [ "--info", "-i"],
                "name_settings": "info"
            },     
            {
                "names": [ "--warnings", "-w"],
                "name_settings": "warn"
            },            
            {
                #TODO
                "names": [ "--volume", "-vol"],
                "name_settings": "volume"
            },
        ]
    },
    {
        "names": [ "skip" ],
        "function": lambda settings: ic(playback.current.skip()),
        "flags": [

        ]
    },
    {
        "names": [ "list_playlists", "lp" ],
        "function": lambda settings: ic(list_playlists(settings)),
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
    }
])

exit_flag = False
playback = PlaybackManager()

def parse_tokens(input, arg_library):
    argument = input.split(' ')[0]
    arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
    if arg_def is None: raise Exception("Specified argument does not exist!")
    # extract the flags and their values from the input string
    flags = re.findall(r"(?<= )-.+?(?=\=\".+?\")", input)
    vals = re.findall(r"(?<=\=\").+?(?=\")", input)

    # merge the regiesterd flags and their values
    # set default values
    flag_mapping = {
        flag_def["name_settings"]: flag_def["default"]
        for flag_def in arg_def["flags"]
        if "default" in flag_def
    }
    # override with custom values, if any
    flag_mapping.update({flag_def["name_settings"]: val
                        for flag, val in zip(flags, vals)
                        for flag_def in arg_def["flags"] 
                        if flag in flag_def["names"]})

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
    info("Type 'help' to retrieve documentation.")
    while exit_flag == False:
        try:
            tokens = ic(input())
            argument, flags = ic(parse_tokens(tokens, arguments.get()))
            ic(handle_arg(argument, flags))
        except  HTTPError as e:
            if debug_mode: 
                raise(e)
            else: 
                warn("An HTTP Error occured.")
                ic(e)
                exit_failure()
        except Exception as e:
            if debug_mode: 
                raise(e)
            else: 
                ic(e)
