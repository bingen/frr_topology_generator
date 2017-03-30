#!/bin/bash

PREFIX=$1
NAME=$2

IFACE=`ip addr show | grep -B 2 "inet $PREFIX" | head -1 | awk '{print $2}' | cut -d':' -f1`
IP=`ip addr show | grep "inet $PREFIX" | awk '{print $2}'`

# remove IP addr
ip addr del $IP dev $IFACE

# set down
ip link set $IFACE down

# rename
ip link set $IFACE name $NAME
