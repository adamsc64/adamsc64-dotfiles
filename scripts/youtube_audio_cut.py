#!/usr/bin/env python3
"""
Turns an audio clip in a Youtube URL into an mp3 file.

Suggested installation of yt-dlp:
    $ pip install yt-dlp
"""
import argparse
import atexit
import json
import re
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
    parser.add_argument("url", help="YouTube URL", type=validate_url)
    parser.add_argument("-s", "--start_time", help="Start time in HH:MM:SS format", default=None)
    parser.add_argument("-e", "--end_time", help="End time in HH:MM:SS format", default=None)
    parser.add_argument("-o", "--output", help="Output file path", default=None)

    args = parser.parse_args()

    failing_prereq = is_any_failing_prereq()
    if failing_prereq:
        print(f"Please install the following prerequisite before running this script: {failing_prereq}")
        exit(1)

    video_title = get_video_title(args.url)
    download_audio(args.url)

    if args.output:
        destination = args.output
    else:
        # Use the video title as the filename, sanitized for filesystem
        safe_filename = sanitize_filename(video_title)
        destination = os.path.join(os.getcwd(), f"{safe_filename}.mp3")

    if args.start_time or args.end_time:
        cut_audio(args.start_time, args.end_time)
        # Move the audio file to the current directory
        shutil.move(TMP_CUT, destination)
    else:
        # Move the original audio file to the current directory
        shutil.move(TMP_RAW_ORIGINAL, destination)

    print(f"Audio file saved to {destination}")


def validate_url(url):
    # Simple regex to check if the URL is a valid YouTube URL
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$'
    )
    if not youtube_regex.match(url):
        raise argparse.ArgumentTypeError(f"Invalid YouTube URL: {url}")
    return url


def is_any_failing_prereq():
    # Check if prerequisites are installed
    for prereq in PREREQUISITES:
        if shutil.which(prereq) is None:
            return prereq
    return None


def get_video_title(url):
    """Fetch the video title from YouTube using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "title", "--no-warnings", url],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # Fallback to a generic name if title extraction fails
        return "audio-capture"


def sanitize_filename(filename):
    """Sanitize filename to be filesystem-safe."""
    # Remove or replace characters that are problematic in filenames
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length to avoid filesystem issues
    if len(filename) > 200:
        filename = filename[:200]
    # Fallback if filename is empty after sanitization
    if not filename:
        filename = "audio-capture"
    return filename


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
    # Print the command to be run
    print(f"Running command: {' '.join(ffmpeg_cmd)}")
    subprocess.run(ffmpeg_cmd, check=True)


if __name__ == "__main__":
    main()
