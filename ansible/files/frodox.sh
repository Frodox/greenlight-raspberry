alias lsd="ls -d */"
alias ls='ls --group-directories-first --color=auto'
alias ll='ls -lFvh'
alias l='ll'
alias la="ll -a"
alias l.='ls -d .*'
alias lz='ls -ZaFv'

s()
{
    tmux \
    new-session "sudo -iu pi bash -c 'cd ~/workspace/spotty; bash -l'" \; \
    new-window "sudo -iu pi bash -c 'tail -f ~/*.log'" \; \
    new-window "sudo -iu pi bash -c 'bash -l'"
    
}

rpmql()
{
    dpkg-query -L $1
}

#common mistypes
alias dc='cd'
alias cd..="cd .."

alias dmesg='dmesg -L -H -P'
alias less='less -R'
alias df='df -Th'
alias du='du -h'

alias gs='git status '
alias ga='git add '
alias gb='git branch '
alias gc='git commit'
alias gp='git pull --rebase; git push'
alias gd='git diff --color'
alias go='git checkout '
alias gk='gitk --all&'
alias gx='gitx --all'

alias got='git '
alias get='git '

EDITOR=vim
