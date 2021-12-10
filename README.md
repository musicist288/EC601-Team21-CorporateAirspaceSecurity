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

For more detailed information, see the [docs](./docs) directory for more
details.

## Software Setup

The work explored here requires both software and hardware. In our exploration
we used Ubuntu and Debian, but any Linux-based OS running version 4.2 or newer
of the kernel will work with the hardware.

The software provided in this repository requires Python. For dependency
management, it's recommended that you install
[poetry](https://python-poetry.org/).

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
hardware, when you are running a program that requires root access, you'll most
likely need to run:

```
sudo $(which python) <program>
```

This will run the virutalenv python with root privileges.


## Setting up Wi-Fi Hardware

In its current state, the Wi-Fi detection system requires an external Wi-Fi
antenna.  The airsec package provides a utility to put the hardware into monitoring mode in `airsec.iface_utils.wifi_set_monitor_mode`.

If you're using the RTL SDR, you'll need to make sure rtl_power is installed for
your Linux distribution. See [rto_power description](./docs/SDR/rtl_power.md)
directory.
