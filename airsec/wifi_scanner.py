#!/usr/bin/env python
from scapy.all import *
import time
from dataclasses import dataclass
import asyncio

RUNNING_TASKS = []


@dataclass
class WifiPacket:
    timestamp: float

    src_addr: str
    recv_addr: str

    dst_addr: str
    rssi: str



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

        print(packet)



async def sniff_interface(iface):
    sniff(iface=iface, prn=get_wifi_packet_info)


if __name__ == "__main__":
    asyncio.run(sniff_interface("wlan0"))
