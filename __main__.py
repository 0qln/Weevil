from pytube import YouTube
from playbackMan import VideoPlaybackManager, PlaylistPlaybackManager, PlaybackManager
from mpWrapper import MediaPlayer
from threadPtr import ThreadPtr
from icecream import ic
from os import getcwd
import os
from sys import argv
import threading
from help import printHelp
import re
from requests import HTTPError
import logging


arg_library = [
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
            }
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
        "names": [ "exit", "close" ],
        "function":lambda settings: ic(exit_success()),
        "flags": [

        ]
    },
    {
        #TODO
        # ex: set --volume=50
        "names": [ "set" ],
        "function": lambda settings: None,
        "flags": [
        
        ]
    },
    {
        "names": [ "skip" ],
        "function": lambda settings: ic(playback.current.skip()),
        "flags": [

        ]
    },
]
exit_flag = False
playback = PlaybackManager()
debug_mode = True if len(argv)>1 and "DEBUG" in argv[1] else False
# debug_mode = True # DEV
if not debug_mode: 
    def log_to_file(message, log_file=os.path.join(getcwd(), "log.txt")):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s') #format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        logging.info(message)
    ic.outputFunction = log_to_file


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


while exit_flag == False:
    try:
        tokens = ic(input())
        argument, flags = ic(parse_tokens(tokens, arg_library))
        ic(handle_arg(argument, flags))
    except  HTTPError as e:
        if debug_mode: 
            raise(e)
        else: 
            print("An HTTP Error occured.")
            ic(e)
            exit_failure()
    except Exception as e:
        if debug_mode: 
            raise(e)
        else: 
            ic(e)
