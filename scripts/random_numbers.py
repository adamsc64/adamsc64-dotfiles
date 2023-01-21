#!/usr/bin/env python3
import random

last_answer = None

while True:
    answer = input("&> ")
    if answer == "" and last_answer:
        answer = last_answer
    try:
        print(random.randint(1, int(answer)))
        last_answer = answer
    except ValueError:
        pass
