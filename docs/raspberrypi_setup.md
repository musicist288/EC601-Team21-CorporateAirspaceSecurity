# Linux/Raspberry Pi Setup

For the prototype, we used a Raspberry Pi 3B+. The setup is pretty straight forward if you use the internal Wi-Fi radio to monitor traffic and have an Ethernet cable connected to be able to install dependencies (python, rtl_power, postgres, etc.) You actaully don't even need the external Wi-Fi antenna if you use it this way since you can can use its internal network card to monitor traffic in the area (but the external card is nice for other reaons-- See [Portal Traffic Monitor](#Portable-Traffic-Monitor))

In the `config/` directory in this repository there are a few config files to help streamline the setup on Linux. Assuming the distro you're using uses systemd, the `airsec-monitor.service` is a systemd service unit that you can install to start and manage the Wi-Fi monitoring service. Similarly, there is a `airsec-web.service` unit for managing the web interface.

All applications provided by the `airsec` package require the `airsec.config.yaml` file to be in the first of the directories below.

1. `$HOME/.local/etc/airsec.config.yaml`
1. `/etc/airsec/airsec.config.yaml`

You can easily extend this list in `airsec/applications/__init__.py`.

## Portable Traffic Monitor

One unnecessary but interesting configuration we used was to make the network
monitor portable. The main issue with portability is that you can't have your
Raspberry Pi connected to an Ethernet cable or power. Solving for power is easy,
you just need a sufficiently powerful battery pack. The lack of network
connectivity is a bit trickier, but still pretty simple.

Raspberry Pis have an onboard radio chipset that supports connecting to Wi-Fi, but Linux allows you to configure any network card as an access point. There are plenty of tutorials out there. This one works pretty well so long as you stop before step 6: https://thepi.io/how-to-use-your-raspberry-pi-as-a-wireless-access-point/

Everything before step 6 sets up your Pi to advertise as a network you can connect to. Everything from that point forward is about bridging packets between the Wi-Fi interface and the Ethernet interface, but that's not what we want here. Remember, the point is to be portable. With this setup, you can connect to your raspberry pi to view the data being collected.

There's one absolute vitally important issue with this situation, Raspberry Pi's do not have a real-time clock (RTC) onboard. They rely on NTP to set the time. So, you can either by a small RTC and configure the OS to use it (Google it), or you can manually set the date when booting the OS.

### What about Internet connectivity?

You might be asking, "what if I need an internet connection when its portable?" Well, with a second external Wi-Fi antenna and a virtual machine, this becomes pretty simple as well. You can setup the second antenna as a network card on a Linux virtual machine, connect it to your Pi and setup a SOCKS-5 proxy to tunnel external requests through your virutal machine (which should be sharing Internet with the host) to pass traffic through. Here's a tutorial on how to setup a SOCKS-5 proxy: https://www.metahackers.pro/ssh-tunnel-as-socks5-proxy/

Once again, setting the correct system time is basically required so that certificate verifications work. (See above for the discussion about RTC or manually setting the datetime.)