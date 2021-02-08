#!/usr/bin/env python
import random

while True:
    answer = raw_input('&> ')
    try:
        print random.randint(1, int(answer))
    except ValueError:
        pass

