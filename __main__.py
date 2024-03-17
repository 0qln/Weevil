import os
from sys import argv
import threading
import re
from requests import HTTPError
import client
import settings
import arguments
import commons
import logging
import Player

# Create a logger object with the name 'root.weevil'
logger = logging.getLogger('root___.weevil_')


def find_matches(pattern, text):
    matches = re.finditer(pattern, text, re.MULTILINE)
    return [match.group() for match in matches]


def parse_tokens(input:str, arg_library):
    logger.info(f"Begin parse_tokens: {input = }")
    try:
        # get the argument and it's definition
        argument = re.findall(r"\A[a-zA-Z_]+", input)[0]
        logger.info(f"{argument = }")
        arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
        logger.debug(f"{arg_def = }")
        if arg_def is None: 
            client.warn(message="Specified argument does not exist!")
            return None, None

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

        if "async" in argument and argument["async"] == False:
            argument["function"](settings)
        else:
            threading.Thread(target=argument["function"], args=[settings], daemon=True).start()
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
            logger.error(f"Failed to execute action #{i}: {action_name}. Error: {e}")


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
       
    playback = Player.PlaybackManager()
    def reset_playback():
        global playback
        playback = Player.PlaybackManager()

    # Initiate Arguments    
    arguments.initiate(
    [
        {
            # Print 'help.txt'
            "names": [ "help", "-h", "--help" ],
            "function": lambda flags: safe(printHelp=lambda: client.printHelp()),
            "flags": [ 

            ]
        },
        {
            # Play a video or playlist
            "names": [ "play" ],
            "function":lambda flags: 
                safe(
                    not_silent=lambda: playback.set_silent(False),
                    allow_load=lambda: playback.set_load(True),
                    load=lambda: playback.load_source(flags.get("url") or flags.get("commons") and commons.storage[flags["commons"]]),
                    init=lambda: playback.init_next(),
                    play=lambda: playback.start_curr()
                ) if flags else
                safe(
                    not_silent=lambda: playback.set_silent(False),
                    allow_load=lambda: playback.set_load(True),
                    play=lambda: playback.start_curr()
                ),
            "flags": [
                {
                    "names": [ "--commons", "-c" ],
                    "name_settings": "commons"
                },
                { 
                    "names": [ "--url", "-u" ],
                    "name_settings":"url"
                }, 
            ]
        },
        {
            # Clear the terminal
            "names": [ "clear", "cls" ],
            "function":lambda flags: safe(clear=lambda: client.clear()),
            "flags": [ 

            ]
        },
        {
            # Pause playback
            "names": [ "pause", "p" ],
            "function":lambda flags: safe(pause=lambda: playback.pause_curr()),
            "flags": [ 

            ]
        },
        {
            # Resume playback
            "names": [ "resume", "r" ],
            "function":lambda flags: safe(resume=lambda: playback.resume_curr()),
            "flags": [

            ]
        },
        {
            # Exit weevil
            "names": [ "exit", "close", "quit" ],
            "function":lambda flags: safe(
                allow_load=lambda: playback.set_load(False),
                reset=lambda: playback.stop_curr(), 
                exit=lambda: exit_success()), 
            "flags": [

            ],
            "async": False
        },
        {
            # Get a setting
            "names": [ "get"],
            "function": lambda flags: safe(get=lambda: settings.get(flags, print_info=True)),
            "flags": [
                # dynamic
                {
                    "names": [ "--key", "-k" ],
                    "name_settings": "key"
                },

                # hardcoded
                {
                    "names": [ "--title_declerations"],
                    "name_settings": "hail"
                },   
                {
                    "names": [ "--info"],
                    "name_settings": "info"
                },     
                {
                    "names": [ "--failures"],
                    "name_settings": "fail"
                },
                {
                    "names": [ "--warnings"],
                    "name_settings": "warn"
                },            
                {
                    "names": [ "--volume", "-vol"],
                    "name_settings": "volume_db"
                },
                { 
                    "names": [ "--output", "-o" ],
                    "name_settings":"output_folder",
                },
                { 
                    "names": [ "--fileType", "-f" ], 
                    "name_settings":"preferred_file_type",
                },
            ]
        },
        {
            # Set a settings
            "names": [ "set" ],
            "function": lambda flags: safe(set=lambda: settings.set(flags, playback)), 
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
                    "names": [ "--title_declerations"],
                    "name_settings": "hail"
                },   
                {
                    "names": [ "--info"],
                    "name_settings": "info"
                },     
                {
                    "names": [ "--failures"],
                    "name_settings": "fail"
                },
                {
                    "names": [ "--warnings"],
                    "name_settings": "warn"
                },            
                {
                    "names": [ "--volume", "-vol"],
                    "name_settings": "volume_db"
                },
                { 
                    "names": [ "--output", "-o" ],
                    "name_settings":"output_folder",
                },
                { 
                    "names": [ "--fileType", "-f" ], 
                    "name_settings":"preferred_file_type",
                },           
            ]
        },
        {
            # Manage frequently used urls
            "names": [ "commons", "customs" ],
            "function": lambda flags: safe(commons_manage=lambda: commons.manage(flags)),
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
                    "names": [ "--custom_name", "--common", "-c" ],
                    "name_settings": "customname"
                }
            ]
        },
        {
            # Play next track
            "names": [ "next", "skip", "s" ],
            "function": lambda flags: safe(
                not_silent=lambda: playback.set_silent(False),
                allow_load=lambda: playback.set_load(True),
                skip=lambda: playback.skip()),
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
            "function": lambda flags: safe(
                not_silent=lambda: playback.set_silent(False),
                allow_load=lambda: playback.set_load(True),
                prev=lambda: playback.prev()),
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
            # save current setting config to disc
            "names": [ "config_save", "conf_s" ],
            "function": lambda flags: safe(save_settings=lambda: settings.save_to_files(flags), save_commons=lambda: commons.save_to_files(flags)),
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
            "function": lambda flags: safe(load_settings=lambda: settings.load_from_files(flags), load_commons=lambda: commons.load_from_files(flags)),
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
            "function": lambda flags: safe(
                print_info=lambda: 
                    client.pbman_info({"playback_man": playback}) if "pbman" in flags else
                    client.playlist_info({"playback_man": playback}) if "playlist" in flags else 
                    client.channel_info({"playback_man": playback}) if "channel" in flags else
                    client.track_info({"playback_man": playback})),
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
                },
                {
                    # current channel
                    # TODO: add official documentation
                    "names": [ "--channel", "-c" ],
                    "name_settings": "channel"
                },
                {
                    # current playback
                    #TODO: add official documentation
                    "names": [ "--playback_manager", "-pbman" ],
                    "name_settings": "pbman"
                }
            ]
        },
        {
            "names": [ "stop", "reset" ],
            "function": lambda flags: safe(
                forbid_load=lambda: playback.set_load(False),
                stop=lambda: playback.stop_curr(),
                clear=lambda: playback.clear(),
                reset=lambda: reset_playback()
            ),
            "flags": [
                {
                }
            ],
            "async": False
        },
        {
            "names": [ "load" ],
            "function": lambda flags: 
                safe(
                    allow_load=lambda: playback.set_load(True),
                    silent=lambda: playback.set_silent("silent" in flags),
                    load=lambda: playback.load_source(flags.get("url") or flags.get("commons") and commons.storage[flags["commons"]]),
                    fetch=lambda: playback.fetch_all(),
                    reset=lambda: playback.set_silent(False)
                ) if "quit" not in flags else 
                safe(
                    quit=lambda: playback.set_load(False)
                ),
            "flags": [
                {
                    "names": [ "--quit", "-q" ],
                    "name_settings": "quit"
                },
                {
                    "names": [ "--silent", "-s"],
                    "name_settings": "silent",
                },
                {
                    "names": [ "--fetch_content", "-fc" ],
                    "name_settings": "fetch",
                },
                {
                    "names": [ "--commons", "-c" ],
                    "name_settings": "commons"
                },
                { 
                    "names": [ "--url", "-u" ],
                    "name_settings": "url"
                },

            ]
        }
        
    ])
    
    exit_flag = False

    # load config
    settings.load_from_files({ "location": os.getcwd() })
    commons.load_from_files({ "location": os.getcwd() })

    client.info(message="Type 'help' to retrieve documentation.")
   
    logger.info("Initialization complete.")
    
    while not exit_flag:
        try:
            # Gather user input
            tokens = client.get_input()
            logger.debug(f"User input: {tokens}")

            argument, flags = parse_tokens(tokens, arguments.get())
            logger.debug(f"Parsed argument: {argument}")
            logger.debug(f"Parsed flags: {flags}")

            if argument is None or flags is None: continue

            try:
                handle_arg(argument, flags)
            except Exception as e:
                logger.error(f"Failed to execute request: {e}")
                client.fail(message="Failed to execute your request. If this continues to happen, consider restarting weevil.")
        except HTTPError as e:
            logger.error(f"Unexpected HTTP Error: {e}")
        except Exception as e:
            logger.error(f"An unknown error occurred: {e}")
            client.fail(message="An unknown error occurred. Consider restarting weevil.")
        
    logger.info("Exiting program.")   
