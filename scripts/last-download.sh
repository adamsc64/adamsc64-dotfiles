#!/bin/bash
realpath "$(ls -1t "$HOME/Downloads"/* | head -n1)"
