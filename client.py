import os, settings, datetime
from icecream import ic
import client
from mpWrapper import MediaPlayer


# # color testing:
# def change_text_color(color_code): return f'\033[{color_code}m'
# for x in range(200): 
#     print(change_text_color(x) + str(x) + " " + "message")


def fail(*messages): 
    for i in range(len(messages)): ic(str(messages[i]))

    if not settings.get("fail") == "true": return
    
    print('\033[31m' + "".join(str(messages[i])+' || ' for i in range(len(messages)-1)) + (messages[-1]) + '\033[0m')
    

def warn(*messages):
    for i in range(len(messages)): ic(str(messages[i]))

    if not settings.get("warn") == "true": return
    
    print('\033[33m' + "".join(str(messages[i])+' || ' for i in range(len(messages)-1)) + (messages[-1]) + '\033[0m')


def hail(value):
    if not settings.get("hail") == "true": return

    print("    -< "+ '\033[01m' + '\033[04m' + value + '\033[0m'+" >-")


def info(*messages): 
    if not settings.get("info") == "true": return
    
    print('\033[01m' + "".join(str(messages[i])+' || ' for i in range(len(messages)-1)) + (messages[-1]) + '\033[0m')


def track_info(settings):
    mp:MediaPlayer = settings["media_player"]
    client.info("   Title: " + str(mp.get_content_title()))
    client.info("   Duration: " + str(datetime.timedelta(seconds=mp.get_duration())))
    client.info("   Status: " + str(mp.state))

def playlist_info(settings):
    client.info("   Title: ")
    client.info("   Track count: ")

def list_playlists(settings):
    for folder in os.listdir(settings["directory"]):
        if not os.path.isdir(folder):
            continue
        if (len(os.listdir(folder)) > 0):
            p_id = folder
            p_name = os.listdir(folder)[0]
            if not os.path.isdir(os.path.join(settings["directory"], p_id, p_name)): continue
            msg = p_name
            if str(settings["show_id"]).lower() == "true":
                msg += " <id:" + p_id + ">"
            info(msg)


def printHelp():
    # print('TODO: Provide link to github, for issues and feedback')
    # print('TODO: link a website documentation i.e. hosted on github')
    try: 
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "help.txt"), "r") as file:
            help_message = file.read()
            info(help_message)
    except FileNotFoundError:
        fail("Error: Help file not found.")
