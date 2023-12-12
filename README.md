# Weevil
**Music streaming CLI**

Weevil offers real-time and pre-fetched playback for playlists and videos. Currently, there are no plans to introduce playback from local files, as numerous tools already cater to this need. Weevil is designed to address specific gaps in software environments rather than reinventing existing solutions.

To optimize network usage, Weevil caches downloaded videos. Users can choose the file type based on what is available on the target servers. It's important to note that Weevil requires an internet connection to provide playback. If no internet connection is available, playback functionality will not be accessible.


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
   - Start playback of a video or playlist.
     
     Flags:
       - `--url`, `-u`: Video or playlist URL.
       - `--output`, `-o`: Output folder (default: current working directory).
       - `--fileType`, `-f`: File type (default: any).
         
     **Example:** `play -u="https://www.youtube.com/watch?v=NCKL58C3W4A"`

## 2. exit, close, quit
   - Exit Weevil. This will automatically save the current setting configurations.
     
     **Example:** `exit`

## 3. pause, p
   - Pause playback.

     **Example:** `pause`

## 4. resume, r
   - Resume playback.
     
     **Example:** `resume`

## 5. clear, cls
   - Clear the terminal.
     
     **Example:** `clear`

## 6. get
   - Retrieve information about settings.
     
     Flags:
       - `--key`, `-k`: Specify the key to get.
     
     or

       - `--title_declerations`, `-t`: Get title declarations.
       - `--info`, `-i`: Get information.
       - `--failures`, `-f`: Get failures.
       - `--warnings`, `-w`: Get warnings.
       - `--volume`, `-vol`: Get current playback volume.
         
     **Examples:** 
       `get --key="info"`
       `get --volume`

## 8. set
   - Configure settings or parameters.

     Flags:
       - `--key`, `-k`: Specify the key to set.
       - `--value`, `-v`: Specify the value to set.
     
     or
     
       - `--title_declerations`, `-t`: Whether or not to show title declarations.
       - `--info`, `-i`: Whether to show information messages or not.
       - `--failures`, `-f`: Whether to show error/failure messages or not.
       - `--warnings`, `-w`: Whether to show warnings or not.
       - `--volume`, `-vol`: Set the playback volume.
     
     **Examples:** 
       `set --key="some_key" --value="new_value"`
       `set -vol "69"`

## 9. next, skip, s
   - Play the next track.
     
     **Example:** `next`

## 10. previous, prev
   - Play the previous track.
     
     **Example:** `previous`

## 11. list_playlists, lp
   - List downloaded playlists.

     Flags:
       - `--directory`, `-dir`: Specify the directory (default: current working directory).
       - `--show_id`, `-si`: Show ID (default: debug mode).
     
     **Example:** `list_playlists --directory="/path/to/directory" --show_id="true"`

## 12. help, -h, --help
   - Display detailed information about commands.

     **Example:** `help`

## 13. config_save, conf_s
   - Save current setting configurations to a file.

     Flags:
       - `--location`, `-l`: Specify config.json file path (default: current working directory).
     
     **Example:** `config_save`

## 14. config_load, conf_l
   - Load setting configurations from a file.

     Flags:
       - `--location`, `-l`: Specify folder path for config.json file (default: current working directory).
     
     **Example:** `config_load`
