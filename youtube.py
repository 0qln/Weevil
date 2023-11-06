
#
# Note that some of these regex are not tested
# [ Python sucks ]
#

import re

def has_playlist_id(url):
    return bool(extract_playlist_id(url))

def has_video_id(url):
    return bool(extract_video_id(url))

def could_be_video_id(id):
    # regex: 64bit Base64 encoded number
    result = re.search(r"[0-9A-Za-z_-]{10}[048AEIMQUYcgkosw]", id)
    return False if result is None else result.group(0) == id

def could_be_channel_id(id):
    # regex: 128bit Base64 encoded number
    result = re.search(r"[0-9A-Za-z_-]{21}[AQgw]", id)
    return False if result is None else result.group(0) == id

def extract_playlist_id(url):
    regex = r"list=([A-Za-z0-9_-]+)"
    result = re.search(regex, url)
    return result.group(1) if result is not None else None

def extract_video_id(url):
    # Use capturing groups to extract the video ID
    regex = r'(?:watch\?v=|embed\/)([A-Za-z0-9_-]+)'
    result = re.search(regex, url)
    return result.group(1) if result is not None else None

