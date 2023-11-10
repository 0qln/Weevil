import os

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
    print('TODO: Show the most common flags first')
    print('TODO: Provide link to github, for issues and feedback')
    print('TODO: Provide examples')
    print('TODO: link the website documentation i.e. hosted on github')
    pass