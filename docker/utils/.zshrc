############# original ###################
# Set up the prompt

#autoload -Uz promptinit
#promptinit
#prompt adam1

#setopt histignorealldups sharehistory
setopt histignorealldups 

# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e
bindkey ';5D' emacs-backward-word
bindkey ';5C' emacs-forward-word

# Keep 1000 lines of history within the shell and save it to ~/.zsh_history:
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

# Use modern completion system
autoload -Uz compinit
compinit

zstyle ':completion:*' auto-description 'specify: %d'
zstyle ':completion:*' completer _expand _complete _correct _approximate
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' menu select=2
eval "$(dircolors -b)"
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list '' 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=* l:|=*'
zstyle ':completion:*' menu select=long
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' use-compctl false
zstyle ':completion:*' verbose true

zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'

############# bingen ###################
# Initialize colors.
autoload -U colors
colors
export GCC_COLORS=1
# colorful less
#export LESS='-R'
#export LESSOPEN='|~/.lessfilter %s'

# Allow for functions in the prompt.
setopt PROMPT_SUBST

# Autoload zsh functions.
fpath=(~/.zsh/functions $fpath)
autoload -U ~/.zsh/functions/*(:t)

# Enable auto-execution of functions.
typeset -ga preexec_functions
typeset -ga precmd_functions
typeset -ga chpwd_functions

# Append git functions needed for prompt.
preexec_functions+='preexec_update_git_vars'
precmd_functions+='precmd_update_git_vars'
chpwd_functions+='chpwd_update_git_vars'

# Set the prompt.
#PROMPT=$'%{${fg[cyan]}%}%B%~%b$(prompt_git_info)%{${fg[default]}%} '
PROMPT=$'[%*]%{\e[0;31m%}%n%{\e[0;0m%}@%{\e[0;37m%}%m%{\e[0;0m%}[%B%h%b]%b$(prompt_git_info)%{${fg[default]}%}:%{\e[0;36m%}%d%{\e[0;0m%}/%# '

#PS1='[%*]%n@%m:%d/%# '
#PROMPT=$'[%*]%{\e[0;34m%}%n%{\e[0;0m%}@%{\e[0;37m%}%m%{\e[0;0m%}[%B%h%b]:%{\e[0;36m%}%d%{\e[0;0m%}/%# '
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
test -s ~/zaliasrc && . ~/zaliasrc

# load profiles from /etc/profile.d
# #  (to disable a profile, just remove execute permission on it)
if [ `ls -A1 /etc/profile.d/ | wc -l` -gt 0 ]; then
   for profile in /etc/profile.d/*.sh; do
      if [ -x $profile ]; then
         . $profile
      fi
   done
   unset profile
fi

export EDITOR=emacsclient

#http://boredzo.org/blog/archives/2016-08-15/colorized-man-pages-understood-and-customized
man() {
    env \
        LESS_TERMCAP_mb=$(printf "\e[1;31m") \
        LESS_TERMCAP_md=$(printf "\e[1;31m") \
        LESS_TERMCAP_me=$(printf "\e[0m") \
        LESS_TERMCAP_se=$(printf "\e[0m") \
        LESS_TERMCAP_so=$(printf "\e[1;44;33m") \
        LESS_TERMCAP_ue=$(printf "\e[0m") \
        LESS_TERMCAP_us=$(printf "\e[1;32m") \
            man "$@"
}
