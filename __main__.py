from pytube import YouTube
from args import handleArg
from mpWrapper import MediaPlayer
from threadPtr import ThreadPtr



# https://clig.dev/#arguments-and-flags
mp = MediaPlayer()
mpThread = ThreadPtr()
print("`exit` to exit")
while True:
    argv = input().split(" ")
    for argi in range(0, len(argv)):
        if (argv[argi][0] == '-'):
            # let the argument handle it's own flags
            pass
        else:
            handleArg(argv, argi, mp, mpThread)
