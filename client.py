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

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

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
def clear_curr_line(): print(" " * os.get_terminal_size().columns, end='\r')
def go_up_lines(amount): print("\033[A" * amount, end='')

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
    # print new message
    output = f"{style(name)}: {style(message)}"
    print(style_reset() + (output) + style_reset())


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

    client.hail(name="Track Info", message=str(track.video.title))
    client.info(name="Title", message=str(track.video.title))
    client.info(name="Author", message=str(track.video.author))
    client.info(name="Duration", message=str(datetime.timedelta(seconds=track.video.length)))
    client.info(name="Publish date", message=str(track.video.publish_date))

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
    client.info(name="Title", message=str(playlist.title))
    client.info(name="Track count", message=str(playlist.length))
    client.info(name="Owner", message=str(playlist.owner))
    client.info(name="Views", message=str(playlist.views))
    
    logger.info("Finish writing playlist info...")


def list_playlists(settings):
    client.hail(name="Saved Playlists", message=settings["directory"])
    for folder in os.listdir(settings["directory"]):
        if not os.path.isdir(folder):
            continue
        if (len(os.listdir(folder)) > 0):
            p_id = folder
            p_name = os.listdir(folder)[0]
            if not os.path.isdir(os.path.join(settings["directory"], p_id, p_name)): continue
            msg = p_name
            client.info(name=(p_id if settings["show_id"] else "Name"), message=msg)


def printHelp():
    try: 
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "help.txt"), "r") as file:
            print(file.read())
    except FileNotFoundError:
        client.fail("Error: Help file not found.")
