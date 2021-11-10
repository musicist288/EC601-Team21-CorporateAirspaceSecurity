import click
from airsec import (
    wifi_scanner,
    db,
    iface_utils,
)

@click.command()
@click.argument("iface")
def run(iface):
    iface_utils.wifi_set_monitor_mode(iface)
    db.init()
    db.setup_database()
    wifi_scanner.sniff_access_points(iface)

if __name__ == "__main__":
    run()
