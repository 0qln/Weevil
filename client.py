import os, settings, datetime
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

def reduce_indent():
    global currIndentLevel
    currIndentLevel -= 1

def increase_indent():
    global currIndentLevel
    currIndentLevel += 1

def override(func, message, name=None):
    go_up_lines(1)
    clear_curr_line()
    func(message, name)

def fail(message, name=None): 
    if not settings.get("fail") == "true": return
    _print(name=(name if name else "FAIL"), message=style_fail(message), style=style_fail)
def style_fail(value) -> str: return '\033[31m' + str(value) + '\033[0m' 
    
def warn(message, name=None):
    if not settings.get("warn") == "true": return
    _print(name=(name if name else "WARN"), message=style_warn(message), style=style_warn)
def style_warn(value) -> str: return '\033[33m' + str(value) + '\033[0m'

def hail(message, name=None):
    if not settings.get("hail") == "true": return
    _print(name=(name if name else "HAIL"), message=style_hail(message), style=style_hail)
def style_hail(value) -> str: return '\033[01m' + str(value) + '\033[0m'

def info(message, name=None): 
    if not settings.get("info") == "true": return
    _print(name=(name if name else "INFO"), message=style_info(message), style=style_info)
def style_info(value) -> str: return '\033[01m' + str(value) + '\033[0m'

def style_none(value) -> str: return str(value)

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


def _print(name, message, style):
    cols = os.get_terminal_size().columns

    indent = get_indent(currIndentLevel)
    cols -= len(indent)
    print(indent, end='')

    # print(get_middle(), end='')

    message = f"{name}: {message}"
    print(style(cap(message, cols)), end='\n')
    

def cap(s, l): return s if len(s)<=l else s[0:l-3]+'...'


def track_info(settings):
    import playbackMan
    pb:playbackMan.PlaybackManager = settings["playback_man"]
    if (pb.playlist_info is None): return
    client.currIndentLevel += 1
    # client.info(name="Title", message=str(pb.))
    # client.info(name="Duration", message=str(datetime.timedelta(seconds=mp.get_duration())))
    # client.info(name="Status", message=str(mp.state))
    client.currIndentLevel -= 1

def playlist_info(settings):
    import playbackMan
    pb:playbackMan.PlaybackManager = settings["playback_man"]
    if (pb.playlist_info is None): return
    client.hail(name="Info", message=pb.playlist_info.playlist.title)
    client.increase_indent()
    client.info(name="Title", message=pb.playlist_info.playlist.title)
    client.info(name="Track count", message=pb.playlist_info.playlist.length)
    client.info(name="Owner", message=pb.playlist_info.playlist.owner)
    client.info(name="Views", message=pb.playlist_info.playlist.views)
    client.reduce_indent()

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
