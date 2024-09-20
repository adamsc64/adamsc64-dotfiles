# .zshenv
#
# Sourced every time a Zsh session starts, regardless of whether it is
# a login, interactive, or non-interactive shell. This means it's read
# for all kinds of Zsh sessions. It is the first file sourced by Zsh
# during startup, even before .zshrc.


PATH=$PATH:~/scripts:~/bin
PATH="/usr/local/opt/openjdk/bin:$PATH"
export PATH

CPPFLAGS="-I/usr/local/opt/openjdk/include"
export CPPFLAGS

alias adb=~/coding/android/platform-tools/adb

[ -f ".zshenv.local" ] && source ".zshenv.local"