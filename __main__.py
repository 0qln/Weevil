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
import commons

def find_matches(pattern, text):
    matches = re.finditer(pattern, text, re.MULTILINE)
    return [match.group() for match in matches]

def parse_tokens(input:str, arg_library):
    # # get the argument and it's definition
    argument = re.findall(r"\A[a-zA-Z_]+", input)[0]
    arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
    if arg_def is None: 
        client.warn(message="Specified argument does not exist!")
        return None, None
    ic(argument)
    ic(input)
    ic(arg_def)

    # search for pseudo legal flags and values in the input string
    flag_values = find_matches(r"(-|--)(\w| )+?(\".+?){2}|-[\w-]+", input + ' ')
    flags = [ find_matches(r"-[a-zA-Z_-]+(?:\b)", str(fv_pair)) for fv_pair in flag_values ]
    values = [ find_matches(r"(?<=\").+(?=\")", str(fv_pair)) for fv_pair in flag_values ]
    ic(flag_values)
    ic(flags)
    ic(values)

    flag_mapping = { }

    # load flags specified by user, if no value load `None`
    [flag_mapping.update({flag_def["name_settings"]: (val[0] if len(val) > 0 else None)})
                        for flag_def in arg_def["flags"]
                        for flag, val in zip(flags, values)
                        if flag[0] in flag_def["names"]]
    
    ic (flag_mapping)

    # merge the regiesterd flags and their values
    # load defaults. if specified, but either the flag wasn't added or no custom value was added
    flag_mapping.update({flag_def["name_settings"]: flag_def["default"] 
                        for flag_def in arg_def["flags"] 
                        if "default" in flag_def and (
                            flag_def["name_settings"] not in flag_mapping or
                            flag_mapping[flag_def["name_settings"]] == None)})
    ic(flag_mapping)


    return arg_def, flag_mapping


def handle_arg(argument, settings):
    if (argument is None): return
    if (settings is None): return
    ic(threading.Thread(target=argument["function"], args=[settings], daemon=True).start())


def exit_success(): 
    ic("Exit success.")
    exit()

def exit_failure(): 
    ic("Exit failure.")
    exit()   

def exit():
    global exit_flag
    exit_flag = True


if __name__ == "__main__":
 
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
                    "names": [ "--commons", "-c" ],
                    "name_settings": "commons"
                },
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
                # TODO: remove UI options
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
            # Manage frequently used urls
            "names": [ "commons", "customs" ],
            "function": lambda settings: ic(commons.manage(settings)),
            "flags": [
                {
                    # Add a frequently used url
                    "names": [ "--add", "-a" ],
                    "name_settings": "add"
                },
                {
                    # Remove a frequently used url
                    "names": [ "--remove", "-r" ],
                    "name_settings": "remove"
                },

                {
                    # List commons,
                    # if either -c or -u specified, only list that
                    "names": [ "--list", "-l" ],
                    "name_settings": "list"
                },

                {
                    # Value
                    "names": [ "--url", "-u" ],
                    "name_settings": "url",
                    "default": ""
                },
                {
                    # Key
                    "names": [ "--custom_name", "-c" ],
                    "name_settings": "customname"
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
                    "default": debug_mode
                }
            ]
        },
        {
            # save current setting config to disc
            "names": [ "config_save", "conf_s" ],
            "function": lambda s: ic(settings.save_to_files(s)) and ic(commons.save_to_files(s)),
            "flags": [
                {
                    # the folder location of that the config files will be generated in
                    "names": [ "--location", "-l" ],
                    "name_settings": "location",
                    "default": os.getcwd(),
                }
            ]
        },
        {
            # load current setting config from disc
            "names": [ "config_load", "conf_l" ],
            "function": lambda s: ic(settings.load_from_files(s)) and ic(commons.load_from_files(s)),
            "flags": [
                {
                    # the file path to the config.json file
                    "names": [ "--location", "-l" ],
                    "name_settings": "location",
                    "default": os.getcwd(),
                }
            ]
        },
        {
            # print info
            "names": [ "info" ],
            "function": lambda s: (client.playlist_info({"playback_man": playback}) if "playlist" in s else client.track_info({"media_player": playback.current})) and ic("Info command executed"),
            "flags": [
                {
                    # current track
                    "names": [ "--track", "-t" ],
                    "name_settings": "track",
                },
                {
                    # current playlist
                    "names": [ "--playlist", "-p" ],
                    "name_settings": "playlist",
                }
            ]
        }
    ])
    
    exit_flag = False

    playback = PlaybackManager()

    # load config
    settings.load_from_files({ "location": os.getcwd() })
    commons.load_from_files({ "location": os.getcwd() })

    client.info(message="Type 'help' to retrieve documentation.")
    
    while exit_flag == False:
        try:
            # Gather user input
            tokens = ic(client.get_input())

            try:
                argument, flags = ic(parse_tokens(tokens, arguments.get()))
                try:
                    ic(handle_arg(argument, flags))
                except Exception as e:
                    ic(e)
                    client.fail(message="Failed to execute your request. If this continues to happen, consider restarting weevil.")
            except Exception as e:
                ic(e)
                client.warn(message="There seems to be something wrong with your input.")
        except  HTTPError as e:
            if debug_mode: 
                raise(e)
            else: 
                ic(e)
                client.fail(message="An HTTP Error occured.")
        except Exception as e:
            if debug_mode: 
                raise(e)
            else: 
                ic(e)
                client.warn(message="An unknown error occured.")
        
    ic("EXIT PROGRAM")
    