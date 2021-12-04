from .. import sdr_scanner, db
from . import load_config

def run():
    config = load_config()

    if not config:
        raise RuntimeError("Config file not found.")

    db.init(config)
    db.setup_database()

    sdr_config = sdr_scanner.SDRScannerConfig(
        lower_freq=config.sdr_lower_freq,
        upper_freq=config.sdr_upper_freq,
        bin_size=config.sdr_bin_size,
        integration_interval_seconds=config.sdr_integration_interval
    )

    if config.sdr_integration_interval is not None:
        sdr_config.integration_interval_seconds = config.sdr_integration_interval

    sdr_scanner.monitor_airspace(sdr_config)

if __name__ == "__main__":
    run()