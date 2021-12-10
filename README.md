# Corporate Airspace Security Detection

This repository contains exploration material and software for building a system
to monitor and analyze wireless network traffic for purpose of identifying
threats in an airspace. It provides an application structure for adding and
analyzing different radio threat data. Currently, there are two systems
implemented that capture data:

1. The Wi-Fi monitor application monitors the airspace for beacon packets
and logs them with a timestamp to a database such that they are searchable.
There is a separate table that stores the allowed list of beacon BSSIDs which
our POC analysis system queries to determine evil twins in the area.

2. The SDR system currently requires an RTL SDR to monitor power measurements
of RF signals that the application is configured to scan. The RF Log should be
augmented to store the metadata necessary to point to raw RF recording for
forensic analysis. The raw RF logs should be stored separately and that portion
has not yet been integrated into the `airsec` package, and potentially requires
a second SDR to record.  In a cloud infrastructure, this should be a cheap blob
storage.

Data analysis can be any module or process that ingests data logged to the
database and produces some way of providing forensic tools or alerting. In
this repository they are exemplified by simple database queries executed
by a web application.

The software in this repository was written to run on a Raspberry Pi 3B+
with external hardware for capturing the radio data. In our system we
used an RTL-SDR and a commodity Wi-Fi antenna to capture data from the
system.


## Software Setup

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

As many of the scripts in the repository require root access to networking
hardware, when you are running a program that requires access, you'll most
likely need to run:

```
sudo $(which python) <program>
```

This will run the virutalenv python with root privileges.


## Setting up Wi-Fi Hardware

In its current state, the Wi-Fi detection system requires an external Wi-Fi
antenna. If you're using Kali, you will need to do the following to put the card
into monitoring mode.  Most of the following steps require root privilege (use
`sudo` or switch to root user).


1. Make sure you see the wireless device: `ifconfig`. If you don't see your
network card:
    a. Find the device name: `ifconfig -a`
    b. `ifconfig <iface> up`
2. Using airmon, put the card into monitoring mode: `airmon-ng start <iface>`
    a. This assumes you are not connecting to an access point and are monitoring
    all 802.11 traffic in the area. If you are trying to monitor on a specific
    network you'll need to use `wpa_supplicant` to connect to the network first.
3. If you need to restart the card for some reason, you can use: `airmon-ng
check kill`, but make sure to restart the network manager: `systemctl start
NetworkManager.service`, otherwise your other interfaces won't be available.


