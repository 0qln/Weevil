import os, settings, datetime
from icecream import ic
import client
from mpWrapper import MediaPlayer


# # color testing:
# def change_text_color(color_code): return f'\033[{color_code}m'
# for x in range(200): 
#     print(change_text_color(x) + str(x) + " " + "message")

_ = '''

Playlist: Music [Muccascade]
    ╦
    ╠══ Current Track: Gloria 1996 (E-Mission Old School Area OST)
    ║
    ╚══ Current Track: Yggdrasil
        ╦
        ╠══ Duration: 2:30
        ║
        ╚══ Artist: Bruno Mars
    ║
    ╠══ Current Track: D-Block & S-te-Fan - Angels and Demons [NXC]
    ║
    ╚══ Track Count: ...


play -c "muccascade"
info --track
info --playlist

'''

currIndentLevel = 0
indentWidth = 4 # default tab with, should be >= 2
newLineSpacing = 0 # space between each line of information

def fail(message, name=None): 
    if not settings.get("fail") == "true": return
    _print(name=get_fail(name if name else "FAIL"), message=get_fail(message))
def get_fail(value) -> str: return '\033[31m' + str(value) + '\033[0m' 
    
def warn(message, name=None):
    if not settings.get("warn") == "true": return
    _print(name=get_warn(name if name else "WARN"), message=get_warn(message))
def get_warn(value) -> str: return '\033[33m' + str(value) + '\033[0m'

def hail(message, name=None):
    if not settings.get("hail") == "true": return
    _print(name=get_hail(name if name else "HAIL"), message=get_hail(message))
def get_hail(value) -> str: return '\033[01m' + str(value) + '\033[0m'

# print in white
def info(message, name=None): 
    if not settings.get("info") == "true": return
    _print(name=get_info(name if name else "INFO"), message=get_info(message))
def get_info(value) -> str: return '\033[01m' + str(value) + '\033[0m'

def get_indent(amount = None) -> str: return " " * indentWidth * (amount if amount else currIndentLevel)
def get_bottom() -> str: return "╚" + "═" * (indentWidth - 2) + " "
def get_middle() -> str: return "╠" + "═" * (indentWidth - 2) + " "

def go_up_lines(amount): print("\033[A" * amount, end='')
def clear_curr_line(): print(" " * os.get_terminal_size().columns, end='\r')

def get_input() -> str:
    # Get the input
    userInput = input() 

    # Delete user input line
    client.go_up_lines(1)
    client.clear_curr_line()

    # Return the input
    return userInput


def set_cursor_position(row, col):
    escape_code = f"\033[{row};{col}H"
    print(escape_code, end='', flush=True)


def _print(name, message):
    print(get_indent(currIndentLevel), end='')

    # print(get_middle(), end='')

    print(f"{name}: {message}", end='\n')
    



def track_info(settings):
    mp:MediaPlayer = settings["media_player"]
    client.currIndentLevel += 1
    client.info(name="Title", message=str(mp.get_content_title()))
    client.info(name="Duration", message=str(datetime.timedelta(seconds=mp.get_duration())))
    client.info(name="Status", message=str(mp.state))
    client.currIndentLevel -= 1

def playlist_info(settings):
    import playbackMan
    pb:playbackMan.PlaybackManager = settings["playback_man"]
    client.info(name="Title", message=pb._playlist.playlist.title)
    client.info(name="Current Track: ", message=pb.current.title)
    client.info(name="Track count", message=pb._playlist.playlist.length)

def list_playlists(settings):
    client.hail(name="Saved Playlists", message=settings["directory"])
    client.currIndentLevel += 1
    for folder in os.listdir(settings["directory"]):
        if not os.path.isdir(folder):
            continue
        if (len(os.listdir(folder)) > 0):
            p_id = folder
            p_name = os.listdir(folder)[0]
            if not os.path.isdir(os.path.join(settings["directory"], p_id, p_name)): continue
            msg = p_name
            client.info(name=(p_id if settings["show_id"] else "Name"), message=msg)
    client.currIndentLevel -= 1


def printHelp():
    try: 
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "help.txt"), "r") as file:
            print(file.read())
    except FileNotFoundError:
        fail("Error: Help file not found.")
