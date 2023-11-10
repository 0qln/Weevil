# https://clig.dev/#arguments-and-flags

# "output_folder":"D:\\Programmmieren\\Projects\\Weevil\\v0\\v1_output_folder_[Testing]\\",
# "url":"https://www.youtube.com/playlist?list=PLlfOcCY7-Rxyl2fU_elKD0_Zv-6Fm-kl2",
# "file_type": '.mp4'

# ppm = PlaylistPlaybackManager({
#     # "url":"https://www.youtube.com/playlist?list=PLlfOcCY7-RxyZ5-OErC7MuV32Qc0JHi0o",
#     "url": "https://www.youtube.com/playlist?list=PLlfOcCY7-RxxAGKtjCtiv4vZs_DnlVvNZ",
#     "output_folder":"D:\\Programmmieren\\Projects\\Weevil\\v0\\v1_output_folder_[Testing]\\",
#     "file_type": '.mp4'
# })
from pytube import YouTube
from playbackMan import VideoPlaybackManager, PlaylistPlaybackManager, PlaybackManager
from mpWrapper import MediaPlayer
from threadPtr import ThreadPtr
from icecream import ic
from os import getcwd
import threading
from help import printHelp
import re



playback = PlaybackManager()


arg_library = [
    {
        "names": [ "help", "-h", "--help" ],
        "function": printHelp,
        "flags": [ 

        ]
    },
    {
        "names": [ "play" ],
        "function":lambda settings: playback.play(settings),
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
        "names": [ "pause" ],
        "function":lambda settings: playback.current.pause(),
        "flags": [ 

        ]
    },
    {
        "names": [ "resume" ],
        "function":lambda settings: playback.current.resume(),
        "flags": [

        ]
    },
    {
        "names": [ "exit", "close" ],
        "function":lambda settings: exit_success(),
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
        "names": [ "resume_play", "toggle_play" ],
        "function": lambda settings: playback.current.toggle_pause()
    }
]


def parse_tokens(input, arg_library):
    argument = input.split(' ')[0]
    arg_def = next((arg for arg in arg_library if argument in arg["names"]), None)
    if arg_def is None: raise Exception("Specified argument does not exist!")
    ic (arg_def)

    # extract the flags and their values from the input string
    flags = re.findall(r"(?<= )-.+?(?=\=\".+?\")", input)
    vals = re.findall(r"(?<=\=\").+?(?=\")", input)
    ic(flags)
    ic(vals)

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

    ic(flag_mapping)

    return arg_def, flag_mapping


def handle_arg(argument, settings):
    # debug
    ic(argument)
    ic(settings)

    # execute
    threading.Thread(target=argument["function"], args=[settings], daemon=True).start()


def exit_success():
    global exit_flag
    exit_flag = True
    

exit_flag = False
while exit_flag == False:
    try:
        tokens = input()
        ic.disable()
        argument, flags = parse_tokens(tokens, arg_library)
        ic.enable()
        handle_arg(argument, flags)
    except Exception as e:
        ic(e)
