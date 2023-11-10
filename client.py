import os, settings, arguments
from icecream import ic

# color testing:
# def change_text_color(color_code): return f'\033[{color_code}m'
# for x in range(200): 
#     print(change_text_color(x) + str(x) + " " + "message")

def fail(*messages): 
    if settings.get("warn") == "true":
        print('\033[31m' + "".join(str(messages[i])+' || ' for i in range(len(messages)-1)) + (messages[-1]) + '\033[0m')
def info(*messages): 
    if settings.get("info") == "true":
        print('\033[01m' + "".join(str(messages[i])+' || ' for i in range(len(messages)-1)) + (messages[-1]) + '\033[0m')

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
            print(msg)


def printHelp():
    # print('TODO: Show the most common flags first')
    # print('TODO: Provide link to github, for issues and feedback')
    # print('TODO: Provide examples')
    # print('TODO: link the website documentation i.e. hosted on github')
    try: 
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "help.txt"), "r") as file:
            help_message = file.read()
            info(help_message)
    except FileNotFoundError:
        fail("Error: Help file not found.")
