import os, settings, datetime, logging
import client
from mpWrapper import MediaPlayer

logger = logging.getLogger(f"root___.weevil_.client_")
logger.info(f"Logging to file enabled.")

_ = '''
INFO: Settings loaded from file: D:\Programmmieren\Projects\Weevil\v0\settings.json
INFO: Commons loaded from file: D:\Programmmieren\Projects\Weevil\v0\commons.json
INFO: Type 'help' to retrieve documentation.
╦
╚══ Playlist: Music [Muccascade]
    ╦
    ╠══ Current Track: Gloria 1996 (E-Mission Old School Area OST)
    ║
    ╠══ Current Track: Yggdrasil
    ║   ╦
    ║   ╠══ Duration: 2:30
    ║   ║
    ║   ╚══ Artist: Bruno Mars
    ║
    ╠══ Current Track: D-Block & S-te-Fan - Angels and Demons [NXC]
    ║
    ╚══ Track Count: ...
|

play -c "muccascade"
info --track
info --playlist

'''

# Public parameters
currIndentLevel = 0
indentWidth = 4 # default tab with, should be >= 2
newLineSpacing = 0 # space between each line of information

# Private caching
CACHE = {}
CACHE["pipe_col"] = -1
CACHE["indent_level"] = -1
CACHE["is_overriding"] = False
CACHE["lines_printed"] = 0


def clear():
    os.system('cls' if os.name=='nt' else 'clear')

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
    output(name=(name if name else "FAIL"), message=style_fail(message), style=style_fail)
def style_fail(value) -> str: return '\033[00m' + '\033[31m' + str(value) + '\033[0m' 
    
def warn(message, name=None):
    if not settings.get("warn") == "true": return
    output(name=(name if name else "WARN"), message=style_warn(message), style=style_warn)
def style_warn(value) -> str: return '\033[00m' + '\033[33m' + str(value) + '\033[0m'

def hail(message, name=None):
    if not settings.get("hail") == "true": return
    output(name=(name if name else "HAIL"), message=style_hail(message), style=style_hail)
def style_hail(value) -> str: return '\033[00m' + '\033[01m' + str(value) + '\033[0m'

def info(message, name=None): 
    if not settings.get("info") == "true": return
    output(name=(name if name else "INFO"), message=style_info(message), style=style_info)
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
    global CACHE
    # Get the input
    set_cursor_position(col=0, row=CACHE["lines_printed"]+2)
    userInput = input(get_indent(currIndentLevel)) 

    # Delete user input line
    client.go_up_lines(1)
    client.clear_curr_line()
    set_cursor_col(0)

    # Return the input
    return userInput


def set_cursor_position(row, col):
    escape_code = f"\033[{row};{col}H"
    print(escape_code, end='', flush=True)

def set_cursor_col(col):
    escape_code = f"\033[{col}G"
    print(escape_code, end='', flush=True)


def output(name, message, style):
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
    if not CACHE["is_overriding"]: CACHE["lines_printed"] += 1
    
    # remember pipe posisiotn
    CACHE["pipe_col"] = len(indent) + 1
    CACHE["indent_level"] = currIndentLevel


def pseudo_no_wrapping(text, padding) -> str:
    logger.info("Add wrap protection...")
    logger.info(f"Input: {text}")
    logger.info(f"Padding: {padding}")
    columns = os.get_terminal_size().columns
    printed_chars = 0
    output = ""
    for char in text:
        next_char = char
        # Assuming non-monospaced characters take up more space than monospaced ones
        mode = settings.get("no_overflow_mode")
        logger.info(f"Mode: {mode}")
        if mode == 1:
            # Cut off more than is enough
            # Some characters can be wider than 2 times the normal width, so no guaranty
            char_width = 2 if len(next_char.encode('utf-8')) > 1 else 1
        elif mode == 2:
            # Replace unknown chars with a �
            char_width = 1
            next_char = r"�" if len(next_char.encode('utf-8')) else next_char
        else:
            # No wrapping protection
            char_width = 1
        
        logger.info(f"'{char}' -> '{next_char}'")
        logger.info(f"Len {1} -> Len {char_width}")

        if printed_chars + char_width <= columns + padding:
            output += next_char
            printed_chars += char_width
        else:
            break
    logger.info(f"Output: {output}")
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


#Testing 
# color testing:
#  def change_text_color(color_code): return f'\033[{color_code}m'
#  for x in range(200): 
    #  print(change_text_color(x) + str(x) + " " + "message")


# On module start
clear()
set_cursor_position(0, 0)

