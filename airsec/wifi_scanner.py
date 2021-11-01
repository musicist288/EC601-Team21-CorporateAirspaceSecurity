#!/usr/bin/env python
from scapy.all import *
import time
import asyncio
import click

from . import (
    logger,
    db
)
from .interfaces import WifiPacket

RUNNING_TASKS = []

WifiPacketQueue = asyncio.Queue()

def get_wifi_packet_info(packet):
    if IP in packet:
        ip = packet.getlayer(IP)
        print(ip.fields)

    if Dot11Beacon in packet:
        timestamp = time.time()
        radiotap = packet.getlayer(RadioTap)
        signal = radiotap.fields['dBm_AntSignal']
        frequency = radiotap.fields['ChannelFrequency']
        rate = radiotap.fields['Rate']
        dot11_fcs = packet.getlayer(Dot11FCS)

        recv_addr = dot11_fcs.fields['addr1']
        src_addr = dot11_fcs.fields['addr2']
        dst_addr = dot11_fcs.fields['addr3']

        beacon = packet.getlayer(Dot11Beacon)
        beacon_payload = beacon.payload
        beacon_ssid = beacon_payload.fields['info'].decode('utf-8')

        wp = WifiPacket(timestamp=timestamp,
                        rssi=signal,
                        src_addr=src_addr,
                        dst_addr=dst_addr,
                        recv_addr=recv_addr)

        try:
            db.add_packet_if_unauthorized(wp)
            logger.debug("Added packet to queue.")
        except asyncio.QueueFull:
            logger.warning("Failed to WiFiPacket, queue full.")

async def sniff_interface(iface):
    sniff(iface=iface, prn=get_wifi_packet_info)


@click.command()
@click.argument("iface")
def monitor(iface):
    asyncio.run(sniff_interface(iface))

if __name__ == "__main__":
    monitor()

