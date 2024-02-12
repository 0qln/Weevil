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


logger = logging.getLogger(f"root___.weevil_.vidhelp")
logger.info(f"Logging to file enabled.")


class VideoHelper:
    @staticmethod
    def get_title(file_path):
        logger.info(f"Retrieving title for file: {file_path}")
        try:
            return os.path.basename(file_path)
        except Exception as e:
            logger.error(f"Error retrieving title for file {file_path}: {e}")
            return None

    @staticmethod
    def is_mp4_corrupt(file_path):
        logger.info(f"Checking if MP4 file is corrupt: {file_path}")
        try:
            ffmpeg.input(file_path).output("null", f="null", loglevel="quiet").run()
        except ffmpeg._run.Error:
            logger.info(f"MP4 file is corrupt: {file_path}")
            return True
        else:
            logger.info(f"MP4 file is not corrupt: {file_path}")
            return False

    @staticmethod
    def create_playback_from_video(video: pytube.YouTube, output_folder, file_type, retries=10) -> str | None:
        logger.info(f"Creating playback for video: {video.title}")
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            logger.info(f"Output folder for playback: {output_folder}")

            folder = os.path.join(output_folder, video.video_id) + "\\"
            logger.info(f"Folder for video: {folder}")

            if os.path.exists(folder):
                logger.info("Fetching from local files...")
                client.info("Fetching from local files...")
                file_path = os.path.join(folder, os.listdir(folder)[0])
                client.info(f"Retrieving '{video.title}' from local file: '{file_path}'...")
            else:
                logger.info("Fetching from servers...")
                client.info("Fetching from servers...")
                file_ext = None if file_type == "any" else file_type
                stream = video.streams.filter(only_audio=True, file_extension=file_ext).first()
                client.info(f"Downloading '{video.title}'...")
                file_path = stream.download(folder)
                logger.info(f"Downloaded file location: {file_path}")

            logger.info("Fetch completed")
            
            if VideoHelper.is_mp4_corrupt(file_path):
                if retries > 0:
                    client.warn(f"'{file_path}' is corrupted. Retrying download...")
                    shutil.rmtree(file_path)
                    return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
                else:
                    # Unable to fetch file
                    client.fail(message=f"'{video.title}' cannot be safely downloaded. " + "No retries left. " + f"'{video.title}' will be skipped.")
            else:
                logger.info(f"Successfully acquired '{video.title}'")
                return file_path

        except AgeRestrictedError as e:
            logger.error(f"Age-restricted error: {e}")
            client.warn(message=f"'{video.title}' is age restricted, and can't be accessed without logging in. " + f"<ID:{video.video_id}>")
        
        # Internal SSLError from pytube. Most at the time it's a network error
        except SSLError as e:
            logger.error(f"SSL error: {e}")
            if retries > 0:
                client.fail(message=f"'{video.title}' could not be downloaded due to a network error. "+ f"Retries left: {str(retries)}")
                time.sleep(0.1)
                return VideoHelper.create_playback_from_video(video, output_folder, file_type, retries - 1)
            else:
                client.fail(message=f"'{video.title}' could not be downloaded due to a network error. "+ "No retries left. " + f"'{video.title}' will be skipped.")

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        return None

    @staticmethod
    def create_playback(url, output_folder, file_type):
        logger.info(f"Creating playback for URL: {url}")
        yt = pytube.YouTube(url)
        return VideoHelper.create_playback_from_video(yt, output_folder, file_type), yt
    

