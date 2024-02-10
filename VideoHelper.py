from pyglet.event import EventDispatcher
from mutagen.mp4 import MP4
import pyglet
import pytube, os, threading, re, enum, time, datetime
import settings, client
from pytube.exceptions import AgeRestrictedError
import pytube.exceptions as pyex
from ssl import SSLError
import ffmpeg
import shutil
import logging
from icecream import ic


class VideoHelper:
    @staticmethod
    def get_title(file_path):
        ic("GET_TITLE:", file_path)
        try:
            return os.path.basename(file_path)
        except Exception as e:
            ic("Error getting title:", e)
            return None

    @staticmethod
    def is_mp4_corrupt(file_path):
        ic("IS_MP4_CORRUPT: Checking if MP4 file is corrupt")
        try:
            ffmpeg.input(file_path).output("null", f="null", loglevel="quiet").run()
        except ffmpeg._run.Error:
            ic("Corrupt file:", file_path)
            return True
        else:
            ic("Non-corrupt file:", file_path)
            return False

    @staticmethod
    def create_playback_from_video(video: pytube.YouTube, output_folder, file_type, retries=10) -> str | None:
        ic("CREATE_PLAYBACK_FROM_VIDEO: Creating playback from video")
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            ic("Output folder:", output_folder)

            folder = os.path.join(output_folder, video.video_id) + "\\"
            ic("Folder:", folder)

            if os.path.exists(folder):
                ic("Fetching from files...")
                client.info("Fetching from files...")
                file_path = os.path.join(folder, os.listdir(folder)[0])
                client.override(client.info, f"Get '{video.title}' from file '{file_path}'...")
            else:
                ic("Fetching from servers...")
                client.info("Fetching from servers...")
                file_ext = None if file_type == "any" else file_type
                stream = ic(video.streams.filter(only_audio=True, file_extension=file_ext).first())
                client.override(client.info, ic(f"Download '{video.title}'..."))
                file_path = stream.download(folder)
                ic("File location:", file_path)

            ic("Fetch completed")
            
            if VideoHelper.is_mp4_corrupt(file_path):
                if retries > 0:
                    client.override(client.warn, f"'{file_path}' is corrupted. Retrying download...")
                    shutil.rmtree(file_path)
                    return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
                else:
                    # Unable to fetch file
                    client.override(client.fail, message=f"'{video.title}' cannot be safely downloaded. " + "No retrys left. " + f"'{video.title}' will be skipped.")
            else:
                ic(f"Successfully acquired '{video.title}'")
                return file_path

        except AgeRestrictedError as e:
            ic("AgeRestrictedError:", e)
            client.override(client.warn, message=f"'{video.title}' is age restricted, and can't be accessed without logging in. " + f"<ID:{video.video_id}>")
        
        # Internal SSLError from pytube. Most at the time it's a network error
        except SSLError as e:
            ic("SSLError: ", e)
            if retries > 0:
                client.override(client.fail, message=f"'{video.title}' could not be downloaded due to a network error. "+ f"Retrys left: {str(retries)}")
                time.sleep(0.1)
                return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
            else:
                client.override(client.fail, message=f"'{video.title}' could not be downloaded due to a network error. "+ "No retrys left. " + f"'{video.title}' will be skipped.")

        except Exception as e:
            ic("Exception:", e)

        return None

    @staticmethod
    def create_playback(url, output_folder, file_type) -> str | None:
        ic("CREATE_PLAYBACK: Creating playback from URL")
        return ic(VideoHelper.create_playback_from_video(pytube.YouTube(url), output_folder, file_type))
 
