import click
import asyncio
from airsec import wifi_scanner, db

@click.command()
@click.argument("iface")
def run(iface):
    db.init()
    db.setup_database()
    el = asyncio.get_event_loop()
    el.run_until_complete(wifi_scanner.sniff_interface(iface))

if __name__ == "__main__":
    run()
