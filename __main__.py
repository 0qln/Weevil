from pytube import YouTube
from playbackMan import VideoPlaybackManager, PlaylistPlaybackManager, PlaybackManager
from mpWrapper import MediaPlayer
from threadPtr import ThreadPtr
from icecream import ic
from os import getcwd
import threading


# https://clig.dev/#arguments-and-flags
playback = PlaybackManager()

# "output_folder":"D:\\Programmmieren\\Projects\\Weevil\\v0\\v1_output_folder_[Testing]\\",
# "url":"https://www.youtube.com/playlist?list=PLlfOcCY7-Rxyl2fU_elKD0_Zv-6Fm-kl2",
# "file_type": '.mp4'


arg_library = [
    {
        "names": [ "help", "-h", "--help" ],
        "function":None,
        "flags": [ 

        ]
    },
    {
        "names": [ "load" ],
        "function": lambda settings: playback.load(settings),
        "flags": [
            {
                "names": [ "--type", "-t" ], #video or playlist?
                "name_settings":"type",
                "default":"video"
            },
            { 
                "names": [ "--url", "-u" ],
                "name_settings":"url"
            },
        ]
    },
    {
        "names": [ "clear" ]
    },
    {
        "names": [ "video" ]
    },
    {
        "names": [ "playlist" ]
    },
    {
        "names": [ "play" ],
        "function":lambda settings: playback.current.play(settings),
        "flags": [
            { 
                "names": [ "--url", "-u" ],
                "name_settings":"url"
            },
            { 
                "names": [ "--output", "-o" ],
                "name_settings":"output_folder",
                "default":getcwd()
            },
            { 
                "names": [ "--fileType", "-f" ], 
                "name_settings":"file_type",
                "default":'.mp4'
            }
        ]
    },
    {
        "names": [ "pause" ],
        "function":lambda: playback.current.pause(),
        "flags": [ 

        ]
    },
    {
        "names": [ "resume" ],
        "function":lambda: playback.current.resume(),
        "flags": [

        ]
    },
    {
        "names": [ "exit", "close" ],
        "function":exit,
        "flags": [

        ]
    },
    {
        #TODO
        # ex: set --volume=50
        "names": [ "set" ],
        "function":NotImplementedError,
        "flags": [
        
        ]
    },
    {
        "names": [ "resume_play", "toggle_play" ],
        "function": lambda: playback.current.toggle_pause()
    }
]



def parse_tokens(input_tokens, arg_library):
    argument = input_tokens.pop(0)

    arg_conf = lambda arg: argument in arg["names"]
    found_arg = next((arg for arg in arg_library if arg_conf(arg)), None)

    if found_arg is None:
        raise Exception("Specified argument does not exist!")

    flag_gen = lambda flag: {"name": flag.split('=')[0], "value": flag.split('=')[1]}
    return found_arg, [flag_gen(flag) for flag in input_tokens]


def handle_arg(argument, flags):
    # debug
    ic(argument)
    ic(flags)

    # construct argument settings
    settings = {}
    for flag in argument["flags"]:
        # write default value to settings, if one is specified
        if "default" in flag:
            settings[flag["name_settings"]] = flag["default"]

        # if the user provided an override for the settings, use that
        for flagV in flags:
            if flagV["name"] in flag["names"]:
                settings[flag["name_settings"]] = flagV["value"]

    ic(settings)

    # execute
    threading.Thread(target=argument["function"], args=[settings], daemon=True).start()


while True:
    try:
        tokens = input().split(' ')
        argument, flags = parse_tokens(tokens, arg_library)
        handle_arg(argument, flags)

    except Exception as e:
        print(e)