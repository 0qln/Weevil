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


# Create a logger object with the name 'root.weevil'
logger = logging.getLogger('root___.weevil_')


def find_matches(pattern, text):
    matches = re.finditer(pattern, text, re.MULTILINE)
    return [match.group() for match in matches]

def parse_tokens(input:str, arg_library):
    try:
        # get the argument and it's definition
        argument = re.findall(r"\A[a-zA-Z_]+", input)[0]
        arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
        if arg_def is None: 
            client.warn(message="Specified argument does not exist!")
            return None, None
        logger.info(f"Parsing tokens for argument: {argument}")
        logger.debug(f"Input: {input}")
        logger.debug(f"Argument definition: {arg_def}")

        # search for pseudo legal flags and values in the input string
        flag_values = find_matches(r"(-|--)(\w| )+?(\".+?){2}|-[\w-]+", input + ' ')
        flags = [ find_matches(r"-[a-zA-Z_-]+(?:\b)", str(fv_pair)) for fv_pair in flag_values ]
        values = [ find_matches(r"(?<=\").+(?=\")", str(fv_pair)) for fv_pair in flag_values ]
        logger.debug(f"Flag values: {flag_values}")
        logger.debug(f"Flags: {flags}")
        logger.debug(f"Values: {values}")

        flag_mapping = { }

        # load flags specified by user, if no value load `None`
        [flag_mapping.update({flag_def["name_settings"]: (val[0] if len(val) > 0 else None)})
                            for flag_def in arg_def["flags"]
                            for flag, val in zip(flags, values)
                            if flag[0] in flag_def["names"]]
        
        logger.debug(f"Flag mapping: {flag_mapping}")

        # merge the regiesterd flags and their values
        # load defaults. if specified, but either the flag wasn't added or no custom value was added
        flag_mapping.update({flag_def["name_settings"]: flag_def["default"] 
                            for flag_def in arg_def["flags"] 
                            if "default" in flag_def and (
                                flag_def["name_settings"] not in flag_mapping or
                                flag_mapping[flag_def["name_settings"]] == None)})
        
        logger.debug(f"Merged flag mapping: {flag_mapping}")

        return arg_def, flag_mapping

    except Exception as e:
        logger.error(f"Error while parsing tokens: {e}")
        return None, None


def handle_arg(argument, settings):
    try:
        if (argument is None): return
        if (settings is None): return
        threading.Thread(target=argument["function"], args=[settings], daemon=True).start()
        logger.info(f"Started handling argument on new daemon: {argument}")
    except Exception as e:
        logger.error(f"Error while handling argument: {e}")


def safe(**actions):
    for i, action_name in enumerate(actions):
        action = actions[action_name]
        try:
            logger.info(f"Begin executing action #{i}: {action_name}")
            action()
            logger.info(f"Finish executing action #{i}: {action_name}")
        except Exception as e:
            logger.error(f"Failed to execute action #{i}: {action_name}")


def exit_success(): 
    logger.info("Exit success.")
    exit()

def exit_failure(): 
    logger.info("Exit failure.")
    exit()   

def exit():
    global exit_flag
    exit_flag = True
    logger.info("Exit program.")

class PaddedLevelFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.rjust(8)
        #  record.name = record.name.ljust(20)
        return super().format(record)

if __name__ == "__main__":
    # Initiate Logging
    logging.getLogger("pytube.helpers").disabled = True

    log_format = '%(asctime)s %(levelname)s  %(name)s - %(message)s'
    log_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "log.txt")
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format=log_format,
                        level=logging.DEBUG)
    
    root_logger = logging.getLogger()
    root_handler = root_logger.handlers[0]
    root_handler.setFormatter(PaddedLevelFormatter(log_format))

    logger.info(f"Logging to file enabled. [{log_file}]")
    
    #  logger.debug("Debug message")
    #  logger.info("Info message")
    #  logger.warn("Warn message")
    #  logger.error("Error message")
    #  logger.fatal("Fatal message")
#  
    # Initiate debug mode 
    DEBUG_MODE = True if len(argv)>1 and "DEBUG" in argv[1] else False   
    logger.info(f"Debug Mode: {DEBUG_MODE}")
       
    # Initiate Arguments    
    arguments.initiate([
        {
            # Print 'help.txt'
            "names": [ "help", "-h", "--help" ],
            "function": lambda __s: safe(printHelp=lambda: client.printHelp()),
            "flags": [ 

            ]
        },
        {
            # Play a video or playlist
            "names": [ "play" ],
            "function":lambda __s: safe(reset=lambda: playback.reset(), play=lambda: playback.play(__s)),
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
            "function":lambda __s: safe(clear=lambda: os.system('cls' if os.name=='nt' else 'clear')),
            "flags": [ 

            ]
        },
        {
            # Pause playback
            "names": [ "pause", "p" ],
            "function":lambda __s: safe(pause=lambda: playback.pause()),
            "flags": [ 

            ]
        },
        {
            # Resume playback
            "names": [ "resume", "r" ],
            "function":lambda __s: safe(resume=lambda: playback.resume()),
            "flags": [

            ]
        },
        {
            # Exit weevil
            "names": [ "exit", "close", "quit" ],
            "function":lambda __s: safe(reset=lambda: playback.reset(), exit=lambda: exit_success()), 
            "flags": [

            ]
        },
        {
            # Get a setting
            "names": [ "get"],
            "function": lambda __s: safe(get=lambda: settings.get(__s, print_info=True)),
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
            "function": lambda __s: safe(set=lambda: settings.set(__s, playback)), 
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
            "function": lambda __s: safe(commons_manage=lambda: commons.manage(__s)),
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
            "function": lambda __s: safe(skip=lambda: playback.skip()),
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
            "function": lambda __s: safe(prev=lambda: playback.prev()),
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
            "function": lambda __s: safe(list_playlists=lambda: client.list_playlists(__s)),
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
            "function": lambda __s: safe(save_settings=lambda: settings.save_to_files(__s), save_commons=lambda: commons.save_to_files(__s)),
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
            "function": lambda __s: safe(load_settings=lambda: settings.load_from_files(__s), load_commons=lambda: commons.load_from_files(__s)),
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
            "function": lambda __s: safe(print_info=lambda: client.playlist_info({"playback_man": playback}) if "playlist" in __s else client.track_info({"playback_man": playback})),
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
   
    logger.info("Initialization complete.")
    
    while not exit_flag:
        try:
            # Gather user input
            tokens = client.get_input()
            logger.debug(f"User input: {tokens}")

            try:
                argument, flags = parse_tokens(tokens, arguments.get())
                logger.debug(f"Parsed argument: {argument}")
                logger.debug(f"Parsed flags: {flags}")

                if not argument or not flags: continue

                try:
                    handle_arg(argument, flags)
                except Exception as e:
                    logger.error(f"Failed to execute request: {e}")
                    client.fail(message="Failed to execute your request. If this continues to happen, consider restarting weevil.")
            except Exception as e:
                logger.warning(f"Error parsing tokens: {e}")
                client.warn(message="There seems to be something wrong with your input.")
        except  HTTPError as e:
            if DEBUG_MODE: 
                raise(e)
            else: 
                logger.error(f"An HTTP Error occurred: {e}")
                client.fail(message="An HTTP Error occurred.")
        except Exception as e:
            if DEBUG_MODE: 
                raise(e)
            else: 
                logger.warning(f"An unknown error occurred: {e}")
                client.warn(message="An unknown error occurred.")
        
    logger.info("Exiting program.")   
