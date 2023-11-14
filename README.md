# Weevil
**Music streaming CLI**

Weevil provides realtime and prefetched playback for playlists and videos. 
As for now, it is not planned to add playback from files, as there are enough such tools and Weevil aims to fill a gap in the software enviroments, not reinvent the wheel. 
Weevil caches the downloaded videos for reduced network traffic. The file type can be chosen from what is available on the target servers. If no internet connection is provided, Weevil cannot provide playback. 


## Requirements
- VLC
    - somwhere around version 2.8.0
    - Make sure you have your EV set up
    - If you are using a 64bit machine, make sure you have that version of VLC installed
- Python v.3.0.0 and above


## Usage
- Download and unzip the repository
- Open any shell and navigate the the downloaded repository
- Run `__main__.py` with Python

Example (Windows PowerShell):
```
cd My/Path/To/Weevil
py __main__.py
```


# Weevil CLI Documentation

## 1. play
   - Play a video or playlist.
     This command initiates playback of a video or playlist from a specified URL.
     
     **Flags:**
       - `--url`, `-u`: Specify the URL of the video or playlist.
       - `--output`, `-o`: Specify the output folder (default: current working directory).
       - `--fileType`, `-f`: Specify the file type (default: any).
       
     **Example:** `play -u="https://www.youtube.com/watch?v=NCKL58C3W4A"`

## 2. exit, close, quit
   - Exit Weevil.
     This command gracefully exits the Weevil application.
     
     **Example:** `exit`

## 3. pause, p
   - Pause playback.
     Pauses the currently playing track or video.
     
     **Example:** `pause`

## 4. resume, r
   - Resume playback.
     Resumes playback of the currently paused track or video.
     
     **Example:** `resume`

## 5. clear, cls
   - Clear the terminal.
     Clears the terminal screen, providing a clean interface.
     
     **Example:** `clear`

## 6. get
   - Get a setting.
     Retrieves information about various settings or configurations.
     
     **Flags:**
       - `--key`, `-k`: Specify the key to get.
       - `--title_declerations`, `-t`: Get title declarations.
       - `--info`, `-i`: Get information.
       - `--failures`, `-f`: Get failures.
       - `--warnings`, `-w`: Get warnings.
     
     **Example:** `get --key="some_key"`

## 7. set
   - Set a setting.
     Configures settings or parameters within the Weevil application.
     
     **Flags:**
       - `--key`, `-k`: Specify the key to set.
       - `--value`, `-v`: Specify the value to set.
       - `--title_declerations`, `-t`: Set title declarations.
       - `--info`, `-i`: Set information.
       - `--failures`, `-f`: Set failures.
       - `--warnings`, `-w`: Set warnings.
       - `--volume`, `-vol`: Set volume (TODO).
     
     **Example:** `set --key="some_key" --value="new_value"`

## 8. next, skip, s
   - Play the next track.
     Advances to and plays the next track in the playlist.

     **Example:** `next`

## 9. previous, prev
   - Play the previous track.
     Goes back to and plays the previous track in the playlist.

     **Example:** `previous`

## 10. list_playlists, lp 
   - Print a list of all downloaded playlists and their videos.
      Lists all downloaded playlists and associated videos with optional details.
      
      **Flags:**
        - `--directory`, `-dir`: Specify the directory (default: current working directory).
        - `--show_id`, `-si`: Show ID (default: debug mode).
      
      **Example:** `list_playlists --directory="/path/to/directory" --show_id="true"`

## 11. help, -h, --help
   - Print this help message.
      Displays detailed information about available commands and their usage.
      
      **Example:** `help`
