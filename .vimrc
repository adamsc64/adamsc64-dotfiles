" My .vimrc file
" Christopher Adams

" automatically reload vimrc when it's saved
"" autocmd BufWritePost .vimrc source %

" Always yank to system-wide clipboard.
set clipboard=unnamed

" Mouse-clicks on the terminal will be proxied from terminal to vim
" application.  As a result, clicking will move the cursor, dragging will
" perform visual highlight, and scrolling will move vim screen up and down.
" To fallback to the old behavior, use alt+click.
set mouse=a

" Make backspace conform to normal expected behavior.
set bs=2

" Move around windows more easily.
map <c-h> <c-w>h
map <c-j> <c-w>j
map <c-k> <c-w>k
map <c-l> <c-w>l

" Move around tabs more easily.
map <Leader>n <esc>:tabprevious<CR>
map <Leader>m <esc>:tabnext<CR>

" Move multiple blocks of code, while retaining visual mode.
vnoremap < <gv
vnoremap > >gv

" Set mapleader
let mapleader = ","

" Map the vim 'sort' function.
vnoremap <Leader>s :sort<CR>

" Enable syntax highlighting in general
filetype plugin indent on
syntax on

" Highlight all search results at once
"" set hlsearch

" Visually display tabs as ^I.
"" set list

" Define some custom search behavior
set ignorecase  " Ignore case in search patterns; see 'smartcase'.
set smartcase   " Do match case if uppercase letters are in string

"""""""""""""""""""
" PYTHON SETTINGS "
"""""""""""""""""""

" Set color scheme.
"
" Color schemes should be *.vim files inside $HOME/.vim/colors/
" Here are two nice ones:
" $ curl http://www.vim.org/scripts/download_script.php?src_id=17973 > ~/.vim/colors/pychimp.vim
" $ curl http://www.vim.org/scripts/download_script.php?src_id=13400 > ~/.vim/colors/wombat256mod.vim
set t_Co=256
" If placed before wombat256mod, this defaults to black.
"" autocmd ColorScheme * highlight Normal ctermbg=black
"" color wombat256mod
color pychimp

" Python tabstops
set expandtab     " Turn all tabs into spaces.
set softtabstop=4 " Number of spaces for 'expandtab' spaces conversion.
set autoindent    " Copy indent from current line when starting a new line.
set shiftwidth=4  " Number of spaces for 'autoindent'.
set tabstop=1     " Number of spaces that a <Tab> in the file counts for.
set smarttab      " Tab means 'next' tabstop, not just insert one tabstop.
set smartindent   " Indents after 'cinwords'.
set shiftround    " Round indent to multiple of 'shiftwidth', e.g. for > and <.

" Python setting for 'smartindent'
set cinwords=if,elif,else,for,while,try,except,finally,def,class

" Easy breakpoint insertion for the ipython debugger
" $ sudo pip install ipdb
map <Leader>b Oimport ipdb; ipdb.set_trace()<C-c>

" Consider .wsgi files as python files.
autocmd BufNewFile,BufRead *.wsgi set filetype=python


" Flag whitespace as irregular if: 1. trailing, 2. ALL tabs.
autocmd ColorScheme * highlight ExtraWhitespace
highlight ExtraWhitespace ctermbg=darkred
autocmd InsertEnter * match ExtraWhitespace /\t\|\s\+\%#\@<!$/
autocmd InsertLeave * match ExtraWhitespace /\t\|\s\+$/

" Replace all trailing whitespace automatically.
"" autocmd BufWritePre *.py normal m`:%s/\s\+$//e

"" Some features to make vim more visual
set number           " Turn on line numbers
set textwidth=79     " Autowrap at character 79.
set nowrap           " Turn off annoying line wrapping appearing on next line
set formatoptions-=t " Don't wrap text being inserted
"set ruler            " Replaced by vim-powerline plugin.

" Subtle, dark gray color column on the right to remind us to stay in 80
" characters.
" See http://vim.wikia.com/wiki/Xterm256_color_names_for_console_Vim
set colorcolumn=80
highlight ColorColumn ctermbg=233

" Turn off the bell
set visualbell t_vb=

" Reread files changed outside of vim if there are no changes inside vim.
set autoread

" Bind 'Q' to (attempt) to automatically format paragraphs, following the rules
" defined at tw and fo.
vmap Q gq
nmap Q gqap

" Huge history
set history=700
set undolevels=700

"""""""""""""""""""""""""""
" PATHOGEN PLUGIN MANAGER "
"""""""""""""""""""""""""""
" Set up the Pathogen plugin manager:
" $ mkdir -p ~/.vim/autoload ~/.vim/bundle
" $ curl -o ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/HEAD/autoload/pathogen.vim
" Then just 'git clone' plugins right into ~/.vim/bundle/ and they will be detected.
call pathogen#infect()


" Settings for vim-powerline
"
" Installs a color bar on the bottom of the screen that indicates mode and
" some environment settings.
" $ pushd ~/.vim/bundle && git clone git://github.com/Lokaltog/vim-powerline.git && popd
set laststatus=2  " Always show the status bar (recommended for powerline)


" Settings for ctrlp
"
" A tool for traversing through code by using Ctrl+P.
" $ pushd ~/.vim/bundle && git clone https://github.com/kien/ctrlp.vim.git && popd
autocmd VimEnter,VimResized * let g:ctrlp_max_height = &lines
set wildignore+=*.pyc
set wildignore+=*_build/*
set wildignore+=*/coverage/*


" Settings for python-mode
"
" $ pushd ~/.vim/bundle && git clone https://github.com/klen/python-mode && popd
map <Leader>g :call RopeGotoDefinition()<CR>
let ropevim_enable_shortcuts = 1
let g:pymode_rope_goto_def_newwin = "vnew"
let g:pymode_rope_extended_complete = 1
let g:pymode_breakpoint = 0
let g:pymode_syntax = 1
let g:pymode_syntax_builtin_objs = 0
let g:pymode_syntax_builtin_funcs = 0

" Settings for omnicomplete
"
" Better navigating through omnicomplete option list
" See http://stackoverflow.com/questions/2170023/how-to-map-keys-for-popup-menu-in-vim
set completeopt=longest,menuone
function! OmniPopup(action)
    if pumvisible()
        if a:action == 'j'
            return "\<C-N>"
        elseif a:action == 'k'
            return "\<C-P>"
        endif
    endif
    return a:action
endfunction
inoremap <silent><C-j> <C-R>=OmniPopup('j')<CR>
inoremap <silent><C-k> <C-R>=OmniPopup('k')<CR>


" Python folding
" $ mkdir -p ~/.vim/ftplugin
" $ wget -O ~/.vim/ftplugin/python_editing.vim http://www.vim.org/scripts/download_script.php?src_id=5492
set nofoldenable

