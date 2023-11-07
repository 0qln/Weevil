from flags import getFlags
from flags import getValue
from pytube.exceptions import AgeRestrictedError
import os
import youtube
import pytube
from threading import Thread
import vlc
import time
from mpWrapper import MediaPlayer, MediaPlayerState
from threadPtr import ThreadPtr



def handleArg(argv, argi, mp:MediaPlayer, mpThread:ThreadPtr):
    flagIndices = getFlags(argv, argi + 1)
    flags = { argv[f] for f in flagIndices }
    arg = argv[argi]

    #debug info
    # print('handle arg: ')
    # print (argv[argi])
    # print('with flags: ') 
    # for flag in flags: print(flag)
    
    if arg == "help" or arg == "-h" or arg == "--help":
        printHelp()
    
    if arg == "set":
        # TODO
        # set --volume=50
        pass

    if arg == "exit":
        exit(0)

    if arg == "skip":
        mp.skip()

    if arg == "pause":
        mp.pause()

    if arg == "resume_play":
        if (mp.is_playing()):
            mp.pause()
        else:
            mp.resume()

    if arg == "resume":
        mp.resume()

    if arg == "play":
        # extract command information
        settings = { 
            "output": os.getcwd() + "/TODO_playlistname/",
            "foobar": "C:\\Program Files\\foobar2000",
        }
        for flag in flags:            
            # playlist url
            if "--url" in flag: settings["url"] = getValue(flag, "--url")
            # output folder in which to put the playlist
            elif "--output" in flag: settings["output"] = getValue(flag, "--output") 
            # path to foobar cli
            elif "--foobar" in flag: settings["foobar"] = getValue(flag, "--foobar")
            #TODO: settings for playlist name generation
            #TODO: settings for selection of file to be downloaded (quality <-> data)

        # stop previous playback
        if (mpThread.getValue() is not None): 
            mp.stop()

        # execute command with gathered information on a seperate thread
        mpThread.setValue(Thread(target=play, args=[settings, mp], daemon=True))
        mpThread.getValue().start()

def play(settings, mp:MediaPlayer) -> None:
    # create folder
    pId = youtube.extract_playlist_id(settings["url"])
    if pId is None: 
        raise Exception("No playlist found.")

    # create playlist folder
    dir = settings["output"] + '/' + pId + "/"
    if not os.path.exists(dir): 
        os.makedirs(dir)
    
    # get playlist 
    p = pytube.Playlist(settings["url"])

    for video in p.videos:
        try:
            # aquire data
            vId = video.video_id
            path = "D:\\Programmmieren\\Projects\\Weevil\\v0\\TODO_playlistname\\PLlfOcCY7-RxzP6JTxByf4gP2NUHtDRCOU\\" + vId
            default_filename = ""
            if not os.path.exists(path):
                print('Downloading ' + vId)
                stream = (video.streams
                          .filter(only_audio=True)
                          .first())
                stream.download(path)     
                default_filename = stream.default_filename           
            else:
                print('Video already downloaded:', vId)
                default_filename = os.listdir(path)[0]
            
            # data playback
            print("Start Playback of " + vId)
            filePath =  path + "\\" + default_filename
            mp.play(filePath)
            time.sleep(0.5)

            # handle player state (1/2)
            while (mp.state == MediaPlayerState.PLAYING or
                   mp.state == MediaPlayerState.PAUSED):
                time.sleep(0.1)

        # handle exceptions
        except AgeRestrictedError:
            print(video.watch_url + " is age-restricted and cannot be downloaded without logging in.")
        except Exception as e:
            print("An unknown error occurred while playing " +video.watch_url+ ":", str(e))

        # handle player state (2/2)
        if (mp.state == MediaPlayerState.STOPPED):
            break
        if (mp.state == MediaPlayerState.SKIPPING):
            continue


def printHelp():
    print('TODO: Show the most common flags first')
    print('TODO: Provide link to github, for issues and feedback')
    print('TODO: Provide examples')
    print('TODO: link the website documentation i.e. hosted on github')
    pass