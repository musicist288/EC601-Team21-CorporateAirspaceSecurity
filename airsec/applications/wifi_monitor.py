from .. import (
    wifi_scanner,
    db,
    iface_utils
)

from . import load_config

def run():
    config = load_config()
    if not config:
        raise RuntimeError("Config file not found.")

    iface_utils.wifi_set_monitor_mode(config.wlan_iface_name)
    db.init(config)
    db.setup_database()
    wifi_scanner.sniff_access_points(config.wlan_iface_name)

if __name__ == "__main__":
    run()
