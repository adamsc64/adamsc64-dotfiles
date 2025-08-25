import os
import subprocess
import time
import pygame
from pathlib import Path
from collections import namedtuple


class TimeStamp:
    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def __str__(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}.{self.milliseconds:03}"

    def to_seconds(self) -> float:
        return self.hours * 3600 + self.minutes * 60 + self.seconds + self.milliseconds / 1000


def get_git_root() -> str:
    return subprocess.check_output([
        "git", "rev-parse", "--show-toplevel"
    ], cwd=os.path.dirname(__file__)).decode().strip()


def get_mp3_path() -> str:
    return os.path.join(get_git_root(), "media", "final_fantasy_iv_prelude.mp3")


# Playback range
Start = TimeStamp(seconds=9)
End = TimeStamp(seconds=115)


def main():
    # Initialize pygame mixer
    print("Initializing pygame mixer...")
    pygame.mixer.init()
    print("Loading music...")
    pygame.mixer.music.load(get_mp3_path())
    while True:
        try:
            pygame.mixer.music.play(start=Start.to_seconds())
            SEGMENT_DURATION = End.to_seconds() - Start.to_seconds()
            time.sleep(SEGMENT_DURATION)
        except KeyboardInterrupt:
            print("\nPlayback stopped by user.")
            pygame.mixer.music.stop()
            break
    pygame.mixer.music.stop()

if __name__ == "__main__":
    main()
