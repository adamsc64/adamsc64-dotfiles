#!/usr/bin/env python3
"""
Turns an audio clip in a Youtube URL into an mp3 file.

Suggested installation of yt-dlp:
    $ pip install yt-dlp
"""
import argparse
import atexit
import shutil
import subprocess
import os
import shutil


TMP_RAW_ORIGINAL = "/tmp/youtube-audio-cut-{}.original.mp3".format(os.getpid())
TMP_CUT = "/tmp/youtube-audio-cut-{}.cut.mp3".format(os.getpid())
PREREQUISITES = ["yt-dlp", "ffmpeg"]


def cleanup():
    # Delete temporary files if they exist
    if os.path.exists(TMP_RAW_ORIGINAL):
        os.remove(TMP_RAW_ORIGINAL)

    if os.path.exists(TMP_CUT):
        os.remove(TMP_CUT)

atexit.register(cleanup)


def main():
    parser = argparse.ArgumentParser(description="Download and cut YouTube audio.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("-s", "--start_time", help="Start time in HH:MM:SS format", default=None)
    parser.add_argument("-e", "--end_time", help="End time in HH:MM:SS format", default=None)

    args = parser.parse_args()

    if not passes_system_check():
        print("Please install the following prerequisites before running this script:")
        for prereq in PREREQUISITES:
            print(f"  - {prereq}")
        exit(1)

    download_audio(args.url)

    if args.start_time or args.end_time:
        cut_audio(args.start_time, args.end_time)
        # Move the audio file to the current directory
        destination = os.getcwd() + "/audio-capture-cut.mp3"
        shutil.move(TMP_CUT, destination)
    else:
        # Move the original audio file to the current directory
        destination = os.getcwd() + "/audio-capture.mp3"
        shutil.move(TMP_RAW_ORIGINAL, destination)

    print(f"Audio file saved to {destination}")


def passes_system_check():
    # Check if prerequisites are installed
    for prereq in PREREQUISITES:
        if shutil.which(prereq) is None:
            return False
    return True


def download_audio(url):
    # Download the YouTube video as an audio file
    download_cmd = [
        "yt-dlp",
        "-o",
        TMP_RAW_ORIGINAL,
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",  # highest
        url,
    ]
    subprocess.run(download_cmd, check=True)


def cut_audio(start_time, end_time):
    # Use ffmpeg to cut the audio file
    ffmpeg_cmd = ["ffmpeg", "-i", TMP_RAW_ORIGINAL]
    if start_time:
        ffmpeg_cmd.extend(["-ss", start_time])
    if end_time:
        ffmpeg_cmd.extend(["-to", end_time])
    ffmpeg_cmd.append(TMP_CUT)
    subprocess.run(ffmpeg_cmd, check=True)


if __name__ == "__main__":
    main()
