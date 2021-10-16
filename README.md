# Corporate Airspace Security Detection

This repository contains exploration material and software for building
a system to monitor and analyze wireless network traffic for purpose
of identifying threats in an airspace.

## Setup

## Software

The work explored here requires both software and hardware. In order to
simplify managing network hardware, we've been using a [Kali
Linux](https://www.kali.org/) setup which has many of the drivers and tools
needed to manage common network interfaces pre-installed.


The software provided in this repository requires Python. For dependency
management, it's recommended that you install [poetry](https://python-poetry.org/).

If you have poetry installed, To get setup:

```
poetry install
```

Then to drop into a shell for the virtual environment:

```
poetry shell
```

If you need to add dependencies, do not use pip directly.

```
poetry add <package name>
```

As many of the scripts in the repository require root access to networking hardware,
when you are running a program that requires access, you'll most likely need to run:

```
sudo $(which python) <program>
```

This will run the virutalenv python with root privileges.


## Setting Wi-Fi Hardware

In it's current state, the Wi-Fi detection system requires an external Wi-Fi antenna. If
you're using Kali, you will need to do the following to put the card into monitoring mode.
Most of the following steps require root privilege (use `sudo` or switch to root user).


1. Make sure you see the wireless device: `ifconfig`. If you don't see your network card:
    a. Find the device name: `ifconfig -a`
    b. `ifconfig <iface> up`
2. Using airmon, put the card into monitoring mode: `airmon-ng start <iface>`
    a. This assume you are not connecting to an access point and are monitoring all
       802.11 traffic in the area. If you are trying to monitor on a specific network
       you'll need to use `wpa_supplicant` to connect to the network first.
3. If you need to restart the card for some reason, you can use: `airmon-ng check kill`, but
   make sure to restart the network manager: `systemctl start NetworkManager.service`, otherwise
   your other interfaces won't be available.

## Program Description

Currently there is a simple program for sniffing Wi-Fi packets and prints them to the console. This
is still a work in progressing getting the data from the packets we're looking for (still learning
scapy's interface). Once you're setup, you can try running the program:

```
sudo $(which python) airsec/wifi_sniffer.py <iface>
```

