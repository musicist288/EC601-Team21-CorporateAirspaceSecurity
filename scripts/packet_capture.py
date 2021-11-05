"""
This script is intended for debugging purposes to capture and record
WiFi packets to a file so they can be inspected or used for unit
tests.
"""

from datetime import datetime

from scapy.all import sniff, wrpcap
import click

from airsec import iface_utils

@click.command()
@click.argument("iface")
@click.option("--output-file", type=str, default=None)
def main(iface, output_file):
    iface_utils.wifi_set_monitor_mode(iface)
    if output_file is None:
        output_file = "pcap_trace_%s.pcap" % datetime.now().strftime("%Y-%m-%h_%H-%M-%S")

    print(f"Capturing packets on {iface}. Logging to {output_file}")
    sniff(iface=iface, prn=lambda pkt: wrpcap(output_file, pkt, append=True))

if __name__ == "__main__":
    main()