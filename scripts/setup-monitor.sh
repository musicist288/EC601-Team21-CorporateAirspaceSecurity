#!/usr/bin/env bash

if [ "$EUID" != 0 ];
then
	echo "Must be run as root!"
	exit 1
fi

if [ -z "$1" ];
then
	echo "Usage: $0 IFACE"
	exit 1
fi

IFACE="$1"
ip link set "$IFACE" down
iw "$IFACE" set monitor control
ip link set "$IFACE" up
