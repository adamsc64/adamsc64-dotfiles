#!/bin/bash

# This script will download and compile vim with native python support.
# Many thanks to Martin Brochhaus' talk at PyCon 2012.

# Prerequisites:
#   Ubuntu: sudo apt-get install build-dep vim
#   MacOS:  Commandline Tools for XCode

hg clone https://vim.googlecode.com/hg/ vim
pushd vim/src/
    ./configure \
        --with-features=huge \
        --enable-pythoninterp \
        --with-python-config-dir=/opt/local/bin/python2.7-config \
        --prefix=$HOME/opt/vim
    make && make install
    mkdir $HOME/bin/
    ln -s $HOME/opt/vim/bin/vim $HOME/bin/vim
popd

mkdir -p $HOME/.vim/colors && pushd $HOME/.vim/colors/
    wget -O python.vim https://github.com/hdima/vim-scripts/blob/master/syntax/python/python.vim
    wget -O wombat256mod.vim http://www.vim.org/scripts/download_script.php?src_id=13400
popd

echo "Your vim is located:"
which vim

echo "Your vim is compiled with options:"
vim --version
