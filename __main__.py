from playbackMan import PlaybackManager
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
import logging



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
    logging.info(f"Parsing tokens for argument: {argument}")
    logging.debug(f"Input: {input}")
    logging.debug(f"Argument definition: {arg_def}")

    # search for pseudo legal flags and values in the input string
    flag_values = find_matches(r"(-|--)(\w| )+?(\".+?){2}|-[\w-]+", input + ' ')
    flags = [ find_matches(r"-[a-zA-Z_-]+(?:\b)", str(fv_pair)) for fv_pair in flag_values ]
    values = [ find_matches(r"(?<=\").+(?=\")", str(fv_pair)) for fv_pair in flag_values ]
    logging.debug(f"Flag values: {flag_values}")
    logging.debug(f"Flags: {flags}")
    logging.debug(f"Values: {values}")

    flag_mapping = { }

    # load flags specified by user, if no value load `None`
    [flag_mapping.update({flag_def["name_settings"]: (val[0] if len(val) > 0 else None)})
                        for flag_def in arg_def["flags"]
                        for flag, val in zip(flags, values)
                        if flag[0] in flag_def["names"]]
    
    logging.debug(f"Flag mapping: {flag_mapping}")

    # merge the regiesterd flags and their values
    # load defaults. if specified, but either the flag wasn't added or no custom value was added
    flag_mapping.update({flag_def["name_settings"]: flag_def["default"] 
                        for flag_def in arg_def["flags"] 
                        if "default" in flag_def and (
                            flag_def["name_settings"] not in flag_mapping or
                            flag_mapping[flag_def["name_settings"]] == None)})
    
    logging.debug(f"Merged flag mapping: {flag_mapping}")

    return arg_def, flag_mapping


def handle_arg(argument, settings):
    if (argument is None): return
    if (settings is None): return
    threading.Thread(target=argument["function"], args=[settings], daemon=True).start()
    logging.info(f"Started handling argument on new daemon: {argument}")

def exit_success(): 
    logging.info("Exit success.")
    exit()

def exit_failure(): 
    logging.info("Exit failure.")
    exit()   

def exit():
    global exit_flag
    exit_flag = True
    logging.info("Exit program.")


if __name__ == "__main__":
    # Initiate Logging
    log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.txt")
    logging.basicConfig( filename=log_file,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    logging.info(f"Logging to file enabled. [{log_file}]")

    # Initiate debug mode 
    DEBUG_MODE = True if len(argv)>1 and "DEBUG" in argv[1] else False   
    logging.info(f"Debug Mode: {DEBUG_MODE}")
    
    # Initiate Arguments    
    arguments.initiate([
        {
            # Print 'help.txt'
            "names": [ "help", "-h", "--help" ],
            "function": lambda settings: client.printHelp(),
            "flags": [ 

            ]
        },
        {
            # Play a video or playlist
            "names": [ "play" ],
            "function":lambda settings: playback.reset() and playback.play(settings),
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
            "function":lambda settings: os.system('cls' if os.name=='nt' else 'clear'),
            "flags": [ 

            ]
        },
        {
            # Pause playback
            "names": [ "pause", "p" ],
            "function":lambda settings: playback.pause(),
            "flags": [ 

            ]
        },
        {
            # Resume playback
            "names": [ "resume", "r" ],
            "function":lambda settings: playback.resume(),
            "flags": [

            ]
        },
        {
            # Exit weevil
            "names": [ "exit", "close", "quit" ],
            "function":lambda settings: exit_success(), #playback.reset()) and 
            "flags": [

            ]
        },
        {
            # Get a setting
            "names": [ "get"],
            "function": lambda s: settings.get(s, print_info=True),
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
            "function": lambda s: settings.set(s, playback), 
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
            "function": lambda settings: commons.manage(settings),
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
            "function": lambda settings: playback.skip(),
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
            # Play previous track
            "names": [ "previous", "prev" ],
            "function": lambda settings: playback.prev(),
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
            "function": lambda settings: client.list_playlists(settings),
            "flags": [
                {
                    "names": [ "--directory", "-dir" ],
                    "name_settings": "directory",
                    "default": getcwd()
                },
                {
                    "names": [ "--show_id", "-si" ],
                    "name_settings": "show_id",
                    "default": DEBUG_MODE
                }
            ]
        },
        {
            # save current setting config to disc
            "names": [ "config_save", "conf_s" ],
            "function": lambda s: settings.save_to_files(s) and commons.save_to_files(s),
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
            "function": lambda s: settings.load_from_files(s) and commons.load_from_files(s),
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
            "function": lambda s: client.playlist_info({"playback_man": playback}) if "playlist" in s else client.track_info({"media_player": playback.current}),
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

    # load config
    settings.load_from_files({ "location": os.getcwd() })
    commons.load_from_files({ "location": os.getcwd() })

    playback = PlaybackManager()

    client.info(message="Type 'help' to retrieve documentation.")
   
    logging.info("Initialization complete.")
    
    while not exit_flag:
        try:
            # Gather user input
            tokens = client.get_input()
            logging.debug(f"User input: {tokens}")

            try:
                argument, flags = parse_tokens(tokens, arguments.get())
                logging.debug(f"Parsed argument: {argument}")
                logging.debug(f"Parsed flags: {flags}")

                try:
                    handle_arg(argument, flags)
                except Exception as e:
                    logging.error(f"Failed to execute request: {e}")
                    client.fail(message="Failed to execute your request. If this continues to happen, consider restarting weevil.")
            except Exception as e:
                logging.warning(f"Error parsing tokens: {e}")
                client.warn(message="There seems to be something wrong with your input.")
        except  HTTPError as e:
            if DEBUG_MODE: 
                raise(e)
            else: 
                logging.error(f"An HTTP Error occurred: {e}")
                client.fail(message="An HTTP Error occurred.")
        except Exception as e:
            if DEBUG_MODE: 
                raise(e)
            else: 
                logging.warning(f"An unknown error occurred: {e}")
                client.warn(message="An unknown error occurred.")
        
    logging.info("Exiting program.")
    
