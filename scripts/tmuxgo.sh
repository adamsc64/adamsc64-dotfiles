#!/bin/bash

SESSION=$1

cd ~/coding/
cd ~/coding/*/$1/.. # Try it out

# if the session is already running, just attach to it.
tmux has-session -t $SESSION
if [ $? -eq 0 ]; then
	echo "Session $SESSION already exists. Attaching."
	sleep 1
	tmux -2 attach -t $SESSION
	exit 0;
fi

# create a new session, named $SESSION, and detach from it
tmux -2 new-session -d -s $SESSION
# better: tmux new-session -d 'vi /etc/passwd' \; split-window -d \; attach

# Now populate the session with the windows you use every day
# Some windows I specifically want at a particular index.
# I always want IRC in window 0 and Email in window 1.

tmux new-window    -t $SESSION:0 -k -n runserver
tmux new-window    -t $SESSION:1 -k -n shell
tmux new-window    -t $SESSION:2 -k -n app
tmux new-window    -t $SESSION:3 -k -n ssh
tmux new-window    -t $SESSION:4 -k -n fabric

tmux select-window -t $SESSION:0
tmux -2 attach -t $SESSION
