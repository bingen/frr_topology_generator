#!/bin/bash

SESSION=`whoami`

SHELL=$1
BASE_PATH=$2
NODE=$3
IP=$4
ZEBRA_CONF_FILES_FOLDER=$5

if [ "$#" -ne 5 ]; then
    echo "Illegal number of parameters"
    exit 1
fi


# http://www.leehodgkinson.com/blog/quickly-setup-multiple-pane-and-multiple-window-sessions-in-your-terminal/

echo "Starting byobu session $SESSION"

# Window index
I=0

# -2: forces 256 colors,
byobu-tmux -2 new-session -d -s $SESSION $SHELL

# Daemon windows
for daemon in 'zebra' 'ospfd' 'bgpd' 'ldpd' 'ospf6d' 'isisd'; do
    I=$((I+1))
    byobu-tmux new-window -t $SESSION:$I -n ${daemon^^} $SHELL
    byobu-tmux send-keys "cd $BASE_PATH/frr" C-m
    byobu-tmux send-keys "./${daemon}/${daemon} -u root -g root -f $BASE_PATH/${ZEBRA_CONF_FILES_FOLDER}/${daemon}-${NODE}.conf" C-m
done;

# Vtysh window
I=$((I+1))
echo "Vtysh"
byobu-tmux new-window -t $SESSION:$I -n 'vtysh' $SHELL
byobu-tmux send-keys "cd $BASE_PATH/frr" C-m
byobu-tmux send-keys "./vtysh/vtysh" C-m

# Set default window
byobu-tmux select-window -t $SESSION:0

# Attach to the session you just created
# (flip between windows with alt -left and right)
#byobu-tmux -2 attach-session -t $SESSION
