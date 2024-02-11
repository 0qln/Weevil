import os, settings, datetime, logging
import client
from mpWrapper import MediaPlayer

logger = logging.getLogger(f"root___.weevil_.client_")
logger.info(f"Logging to file enabled.")


# color testing:
#  def change_text_color(color_code): return f'\033[{color_code}m'
#  for x in range(200): 
    #  print(change_text_color(x) + str(x) + " " + "message")
#  
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
    global CACHE
    CACHE["is_overriding"] = True
    go_up_lines(1)
    clear_curr_line()
    func(message, name)
    CACHE["is_overriding"] = False

def style_reset() -> str: return '\033[0m'

def fail(message, name=None): 
    if not settings.get("fail") == "true": return
    _print(name=(name if name else "FAIL"), message=style_fail(message), style=style_fail)
def style_fail(value) -> str: return '\033[00m' + '\033[31m' + str(value) + '\033[0m' 
    
def warn(message, name=None):
    if not settings.get("warn") == "true": return
    _print(name=(name if name else "WARN"), message=style_warn(message), style=style_warn)
def style_warn(value) -> str: return '\033[00m' + '\033[33m' + str(value) + '\033[0m'

def hail(message, name=None):
    if not settings.get("hail") == "true": return
    _print(name=(name if name else "HAIL"), message=style_hail(message), style=style_hail)
def style_hail(value) -> str: return '\033[00m' + '\033[01m' + str(value) + '\033[0m'

def info(message, name=None): 
    if not settings.get("info") == "true": return
    _print(name=(name if name else "INFO"), message=style_info(message), style=style_info)
def style_info(value) -> str: return '\033[00m' + '\033[03m' + str(value) + '\033[0m'

def style_none(value) -> str: return str(value)

def get_indent(amount = None, pipe=False) -> str: 
    return " " * indentWidth * ((amount if amount else currIndentLevel) - (1 if pipe else 0))
def get_bottom_pipe(indentLevel) -> str: 
    return "╚" + "═" * (indentWidth - 2) + " " if indentLevel > 0 else ""
def get_middle_pipe(indentLevel) -> str: 
    return "╠" + "═" * (indentWidth - 2) + " " if indentLevel > 0 else ""
#  def get_root_pipe(indentLevel) -> str:
    #  return " " + "═" * (indentWidth - 2) + " " if indentLevel > 0 else ""
#  
def go_up_lines(amount): print("\033[A" * amount, end='')
def go_down_lines(amount): print("\033[B" * amount, end='')
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

def set_cursor_col(col):
    escape_code = f"\033[{col}G"
    print(escape_code, end='', flush=True)


CACHE = {}
CACHE["pipe_col"] = -1
CACHE["indent_level"] = -1
CACHE["is_overriding"] = False

def _print(name, message, style):
    global CACHE    

    # update prev pipe
    if (CACHE["indent_level"] > 0 
        and CACHE["indent_level"] == currIndentLevel 
        and CACHE["is_overriding"] == False):
        set_cursor_col(CACHE["pipe_col"])
        go_up_lines(1)
        print(get_middle_pipe(currIndentLevel))

    # print new message
    padding=(len(style("")) + len(style("")))
    indent = get_indent(currIndentLevel, pipe=True)
    pipe = get_bottom_pipe(currIndentLevel)
    output = f"{indent}{pipe}{style(name)}: {style(message)}"
    print(style_reset() + pseudo_no_wrapping(output, padding) + style_reset())
    
    # remember pipe posisiotn
    CACHE["pipe_col"] = len(indent) + 1
    CACHE["indent_level"] = currIndentLevel


def pseudo_no_wrapping(text, padding) -> str:
    columns = os.get_terminal_size().columns
    printed_chars = 0
    output = ""
    for char in text:
        # Assuming non-monospaced characters take up more space than monospaced ones
        char_width = 2 if len(char.encode('utf-8')) > 1 else 1
        if printed_chars + char_width <= columns + padding:
            output += char
            printed_chars += char_width
        else:
            break
    return output



def track_info(settings):
    from Track import Track
    from playbackMan import PlaybackManager, ContentType

    logger.info("Start writing track info...")

    pb = settings["playback_man"]
    track:Track = pb.get_current()
    if pb is None: return
    logger.info(f"PlaybackManager: {pb}")
    if track is None: return
    logger.info(f"Track: {track}")
    if track.video is None: return
    logger.info(f"Track.video: {track.video}")

    client.increase_indent()
    client.hail(name="Track Info", message=str(track.video.title))
    client.increase_indent()
    client.info(name="Title", message=str(track.video.title))
    client.info(name="Author", message=str(track.video.author))
    client.info(name="Duration", message=str(datetime.timedelta(seconds=track.video.length)))
    client.info(name="Publish date", message=str(track.video.publish_date))
    client.reduce_indent()
    client.reduce_indent()

    logger.info("Finish writing track info...")


def playlist_info(settings):
    from playbackMan import PlaybackManager

    logger.info("Start writing playlist info...")
    pb:PlaybackManager = settings["playback_man"]
    if pb.playlist_info is None:
        logger.info("No playlist information available.")
        return
    
    playlist = pb.playlist_info.playlist
    logger.info(f"PlaybackManager: {pb}")
    logger.info(f"Playlist: {playlist}")
    
    client.hail(name="Playlist Info", message=playlist.title)
    client.increase_indent()
    client.info(name="Title", message=str(playlist.title))
    client.info(name="Track count", message=str(playlist.length))
    client.info(name="Owner", message=str(playlist.owner))
    client.info(name="Views", message=str(playlist.views))
    client.reduce_indent()
    
    logger.info("Finish writing playlist info...")

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
