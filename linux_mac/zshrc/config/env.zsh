prepend() {
  [ -d "$1" ] && PATH="$1:$PATH"
}
#prepend '/usr/local/bin'
#prepend "$HOME/bin"
prepend '$HOME/.dotfiles/bin'

unset prepend
export PATH

