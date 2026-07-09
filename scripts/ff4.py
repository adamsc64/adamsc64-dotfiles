import argparse
import os
import subprocess
import time
from pathlib import Path

import pygame


class TimeStamp:
    def __init__(
        self, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0
    ):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def __str__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}.{self.milliseconds:03}"

    def to_seconds(self) -> float:
        return (
            self.hours * 3600
            + self.minutes * 60
            + self.seconds
            + self.milliseconds / 1000
        )


def get_git_root() -> str:
    return (
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(__file__)
        )
        .decode()
        .strip()
    )


TRACKS = {
    "ff4": {
        "path": "final_fantasy_iv_prelude.mp3",
        "start": TimeStamp(seconds=9),
        "end": TimeStamp(seconds=120),
    },
    "ff9": {
        "path": "final_fantasy_ix_overworld.mp3",
        "start": TimeStamp(seconds=0),
        "end": None,
    },
}


def get_track_path(track: str) -> str:
    return os.path.join(get_git_root(), "media", TRACKS[track]["path"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Play FF4 prelude or FF9 overworld theme"
    )
    parser.add_argument(
        "track",
        nargs="?",
        choices=sorted(TRACKS.keys()),
        default="ff4",
        help="Track to play (default: ff4)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    track = args.track
    start = TRACKS[track]["start"]
    end = TRACKS[track]["end"]

    mp3_path = get_track_path(track)
    if not Path(mp3_path).is_file():
        raise FileNotFoundError(f"Missing track file: {mp3_path}")

    # Initialize pygame mixer
    print("Initializing pygame mixer...")
    pygame.mixer.init()
    print(f"Loading {track.upper()} track from {mp3_path}...")
    pygame.mixer.music.load(mp3_path)
    while True:
        try:
            pygame.mixer.music.play(start=start.to_seconds())

            if end is None:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                segment_duration = end.to_seconds() - start.to_seconds()
                time.sleep(segment_duration)
        except KeyboardInterrupt:
            print("\nPlayback stopped by user.")
            pygame.mixer.music.stop()
            break
    pygame.mixer.music.stop()


if __name__ == "__main__":
    main()
