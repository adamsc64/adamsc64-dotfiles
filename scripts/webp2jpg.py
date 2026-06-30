#!/usr/bin/env python
'''
Given a set of filenames of images, converts these images into a jpg
and save in the same directory.
'''
import argparse
import os
import sys

from PIL import Image
 

def main(args):
    for filename in args.files:
        img = Image.open(filename)
        img = img.convert('RGB')
        basename, ext = os.path.splitext(filename)
        jpgname = basename + '.jpg'
        if os.path.exists(jpgname) and not args.ignore:
            raise AlreadyExists(jpgname)
        img.save(jpgname)
        print(jpgname)
        if args.delete:
            os.remove(filename)


class AlreadyExists(Exception):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    parser.add_argument('--delete', action='store_true')
    parser.add_argument('--ignore', action='store_true')
    main(parser.parse_args())
