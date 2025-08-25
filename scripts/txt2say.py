#!/usr/bin/env python
"""
Script to speak text from stdin or from filenames given as arguments.

Usage example:
    $ cat chapter1.txt | txt2say
    $ txt2say chapter1.txt

Installation:
    - Install python libraries:
    $ pip install gtts pydub

    - Install mplayer to play audio:
    $ brew install mplayer
"""
from pathlib import Path
import argparse
import fileinput
import os
import sys
import tempfile


try:
    from gtts import gTTS
except ImportError:
    sys.exit("The gtts python library is required.")

try:
    import pydub
    import pydub.playback
except ImportError:
    sys.exit("The pydub python library is required.")


def main():
    files = [args.filename] if args.filename else []
    text = [line.strip() for line in fileinput.input(files=files) if line.strip()]
    text = "\n".join(text)
    if args.sample:
        text = text[:400]
    if args.outfile:
        filename = args.outfile
        save(text, filename)
    else:
        filename = get_tempfile_name()
        save(text, filename)
        play(filename)
        remove(filename)


def save(text, outfile):
    recorder = gTTS(text=text, slow=False)  # , lang=language, slow=False)
    log(f"Saving {outfile}...")
    recorder.save(outfile)
    if args.use_pydub:
        log(f"Speeding up {outfile}...")
        seg = pydub.AudioSegment.from_file(outfile)
        seg = seg.speedup(args.speedup)
        log(f"Resaving {outfile}...")
        seg.export(outfile)


def play(filename):
    log(f"Playing {filename}...")
    if args.use_pydub:
        pydub.playback.play(seg)
        return
    # default to mplayer
    command = f"mplayer -noar -af scaletempo -speed {args.speedup} {filename}"
    if args.verbose:
        os.system(f"{command}")
    else:
        os.system(f"{command} > /dev/null")


def remove(filename):
    log(f"Removing {filename}...")
    os.remove(filename)


def log(text):
    if args.verbose:
        print(text)


def get_tempfile_name():
    prefix = Path(__file__).name + "-"
    tmproot = "/tmp/" if os.path.isdir("/tmp") else tempfile.gettempdir()
    return os.path.join(
        tmproot, prefix + next(tempfile._get_candidate_names()) + ".mp3"
    )


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.strip().split(".")[0])
    parser.add_argument("filename", nargs="?", help="source text file")
    parser.add_argument(
        "--verbose", action="store_true", help="don't print result to stdout"
    )
    parser.add_argument("--speedup", type=float, default=1.5, help="speedup factor")
    parser.add_argument(
        "-o", "--outfile", type=str, help="save the file instead of playing immediately"
    )
    parser.add_argument(
        "--use-pydub",
        action="store_true",
        help="experimental: speedup with pydub instead of mplayer",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="only convert a small sample (mostly for debugging)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main()
