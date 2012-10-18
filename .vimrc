" My .vimrc file
" Christopher Adams

" automatically reload vimrc when it's saved
au BufWritePost .vimrc source %

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
filetype off
filetype plugin indent on
syntax on

" Color schemes should be *.vim files inside $HOME/.vim/colors/
set t_Co=256
color wombat256mod

" Python tabstops
set shiftwidth=4
set softtabstop=4
set tabstop=4
set smarttab
set expandtab
set autoindent
set shiftround

" Flag trailing whitespace
"" autocmd ColorScheme * highlight ExtraWhitespace ctermbg=red guibg=red
"" au InsertLeave * match ExtraWhitespace /\s\+$/    
"" autocmd BufWritePre *.py normal m`:%s/\s\+$//e

" Set color scheme.
" These schemes should be .vim files inside $HOME/.vim/colors/
set t_Co=256
color wombat256mod

" Some features to make vim more like an IDE.
set number  " Line numbers
set tw=79   " 79 characters wide
set nowrap  " Get rid of annoying vim wrapping behavior
set fo-=t   " Don't wrap text being inserted
set colorcolumn=80
"set ruler  " Replaced by vim-powerline plugin.
highlight ColorColumn ctermbg=4

" Binding to automatically format paragraphs, following the rules defined at tw                                                                            
" and fo.                                                                                                                                                  
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
" Clone plugins right into a .vim/bundle/ and they will be detected.
call pathogen#infect()


" vim-powerline
" Installs a color bar on the bottom of the screen that indicates mode and
" some environment settings.
" $ pushd ~/.vim/bundle && git clone git://github.com/Lokaltog/vim-powerline.git && popd
set laststatus=2


" ctrlp
" A tool for traversing through code by using Ctrl+P.
" $ pushd ~/.vim/bundle && git clone https://github.com/kien/ctrlp.vim.git && popd
let g:ctrlp_max_height = 30
set wildignore+=*.pyc
set wildignore+=*_build/*
set wildignore+=*/coverage/*

" Settings for python-mode
" $ pushd ~/.vim/bundle && git clone https://github.com/klen/python-mode && popd
map <Leader>g :call RopeGotoDefinition()<CR>
let ropevim_enable_shortcuts = 1
let g:pymode_rope_goto_def_newwin = "vnew"
let g:pymode_rope_extended_complete = 1
let g:pymode_breakpoint = 0
let g:pymode_syntax = 1
let g:pymode_syntax_builtin_objs = 0
let g:pymode_syntax_builtin_funcs = 0
map <Leader>b Oimport ipdb; ipdb.set_trace() # BREAKPOINT<C-c>

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



