# "global" system stuff

#export LC_ALL='en_US.UTF-8'
#export LANG='en_US.UTF-8'
#export LANGUAGE='en_US.UTF-8'

if hash getconf 2>/dev/null; then
  PATH="$(getconf PATH)"
fi
prepend() {
  [ -d "$1" ] && PATH="$1:$PATH"
}

prepend "$HOME/.dotfiles/linux_mac/bin"

unset prepend

export PATH
