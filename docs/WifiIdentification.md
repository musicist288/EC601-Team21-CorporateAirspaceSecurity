# Wi-Fi Device Identification

### Overview

One of the main functions of our product for securing corporate airspace is to
detect and identify unauthorized Wi-Fi devices in the area that may pose a
threat.  While the long-range vision for our product is to have an SDR that is
capable of decoding Wi-Fi packets, for V1 we are electing to use commodity Wi-Fi
hardware so that we can build the software services needed to discern and alert
threats from authorized Wi-Fi traffic.

### Hardware Selection

In order to simplify our application we decided to focus on the 2.4 GHz Wi-Fi
spectrum. After some searching we came decided on the [LB-Link 150Mbps Wireless
N USB Adapter](http://www.lb-link.cn/products-detail.php?ProId=23). This cheap
Wi-Fi receiver operates in the required frequency range and has the benefit that
it is supported by all major operating systems. This includes Linux based OSes
as long as the running kernel version is 4.2 or newer. This will allow us to
easily develop and test our modules on our laptops before running it on our
prototype (making testing and debugging easier). The prototype will run our
software on a Raspberry Pi with an Ubuntu base operating system.

### Software Selection

As the operating system provides the low-level drivers to use the device, it
leaves us open to using any open-source software solution for parsing the Wi-Fi
packets. After examining a variety of open-source projects, we found the python
library [Scapy](https://scapy.net/) offers a robust set of APIs and bundled
applications for ingesting Wi-Fi packets. Using this, we can stream
data about Wi-Fi traffic in the area to our software that will can decide to
capture or act on the data according to business logic of our application (not
specified here).

### Evil-Twin Detection

Beacon packets are logged to a database in order to be able to detect "evil
twin" attacks where an attacker sets up a malicious access point with the same
SSID as a trusted network. By logging the packets, we can use database queries
to select for beacon packets with SSIDs that are the same as our allow list but
where the BSSIDs do not match.
