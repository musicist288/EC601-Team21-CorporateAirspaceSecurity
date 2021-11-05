#!/usr/bin/env python
import time
from datetime import datetime
from threading import Thread

from scapy.all import (
    AsyncSniffer,
    Dot11Beacon,
    RadioTap,
    conf
)

from . import (
    logger,
    db,
    iface_utils
)
from enum import IntEnum

class PacketType(IntEnum):
    MANAGEMENT = 0
    CONTROL = 1
    DATA = 2
    EXTENSION = 3


class ManagementPacketSubtype(IntEnum):
    ASSOCIATION_REQUEST = 0
    ASSOCIATION_RESPONSE = 1
    REASSOCIATION_REQUEST = 2
    REASSOCIATION_RESPONSE = 3
    PROBE_REQUEST = 4
    PROBE_RESPONSE = 5
    TIMING_ADVERTISEMENT = 6
    # RESERVED = 7
    BEACON = 8
    ATIM = 9
    DISASSOCIATION = 10
    AUTHENTICATION = 11
    DEAUTHENTICATION = 12
    ACTION = 13
    NACK = 14
    # RESERVED2 = 15

beacons = {}

def log_beacon_packets(packet):
    if packet.type != PacketType.MANAGEMENT or packet.subtype != ManagementPacketSubtype.BEACON:
        # We don't care about non-beacon packets
        return

    if Dot11Beacon not in packet:
        raise TypeError("Beacon type packet does not have Dot11Beacon Layer")


    # This IS NOT the 802.11 beacon timestamp (i.e. the number of microseconds the AP has
    # been active.) This is a timestamp of when this program received it.
    timestamp = datetime.now()
    radiotap = packet.getlayer(RadioTap)
    rssi = int(radiotap.fields['dBm_AntSignal'])
    beacon = packet.getlayer(Dot11Beacon)
    # In beacon frames, addr3 is the BSSID
    # https://mrncciew.files.wordpress.com/2014/10/cwap-mgmt-beacon-01.png
    bssid = packet.addr3
    ssid = beacon.network_stats().get('ssid', None)
    channel = beacon.channel
    if "\x00" in ssid:
        logger.warning("SSID contained null bytes, omitting SSID from database: (%s, %s)",
                       bssid,
                       ssid[0:min(10, len(ssid))])
        ssid = None


    db.BeaconPacket.add(
        timestamp,
        bssid,
        ssid,
        channel,
        rssi,
        bytes(packet))

def run_sniffer(*args, **kwargs):
    # This is a hack. The async sniffer built into scapy will seemingly wait and
    # poll forever even when a socket becomes stale due to a hardware failure.
    # Setting `debug_dissector` >= 2 causes the sniffer to re-raise the
    # encountered exception so we can detect it and restart it. This isn't
    # specific to the sniffer unfortunately and there is one global config for
    # all of scapy, so beware. This could enable exceptions elsewhere. Also, the
    # number is a magic constant from the source code, though sometimes this
    # value is assigned a boolean...and there is no documentation about what the
    # different values mean. Anyway, that's a lot of context for a single assingment
    # statement, but that's why this thing is set to 2 here.
    conf.debug_dissector = 2

    sniffer = AsyncSniffer()
    while True:
        try:
            sniffer._run(*args, **kwargs)
        except Exception as ex:
            logger.error("AsyncSniffer raised an exception: %s", ex)


def sniff_access_points(iface: str):
    """
        Function for sniffing WiFi traffic for access points in the area.
        Access points will be logged to the configured database.

        This function requires that the interface already be set to monitor
        traffic, and will run forver.

        Args:
            iface
                The interface name used to scan
    """
    thread = Thread(target=run_sniffer, kwargs=dict(iface=iface, prn=log_beacon_packets))
    thread.start()

    # Start scanning on channel 1
    channel = 1
    while True:
        iface_utils.wifi_set_channel(iface, channel)
        time.sleep(1)
        # "Hop" to the next channel so we capture devices operating on all channels.
        channel += 1
        if channel >= 12:
            channel = 1
