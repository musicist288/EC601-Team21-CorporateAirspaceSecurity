from typing import Optional
from dataclasses import dataclass
import subprocess
import dateutil.parser
from . import db

@dataclass
class SDRScannerConfig:
    lower_freq: str
    upper_freq: str
    bin_size: str
    integration_interval_seconds: int = 10
    tuner_gain: Optional[int] = None


def parse_rtl_power_line(line: str):
    columns = [
        "date",
        "time",
        "hz_low",
        "hz_high",
        "hz_step",
        "num_samples"
    ]

    data = [s.strip() for s in line.split(",")]
    dbms = [float(d) for d in data[len(columns)+1:]]
    params = dict(zip(columns, data[0:len(columns)]))

    for col in ['hz_low', 'hz_high', 'hz_step']:
        params[col] = float(params[col])

    frequencies = [params['hz_low'] + i*params['hz_step'] for i in range(len(dbms))]
    freq_data = dict(zip(frequencies, dbms))
    params['freq'] = freq_data
    params['datetime'] = dateutil.parser.parse(params['date'] + 'T' + params['time'])

    return params


def monitor_airspace(config: SDRScannerConfig):
    args = [
        "/usr/bin/rtl_power",
        "-f", f"{config.lower_freq}:{config.upper_freq}:{config.bin_size}",
        "-i", f"{config.integration_interval_seconds}"
    ]

    if config.tuner_gain is not None:
        args += ["-g", f"{config.tuner_gain}"]

    proc = subprocess.Popen(args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    while True:
        line = proc.stdout.readline().decode()
        if proc.poll() is not None and line == "":
            print("SDR Exited with return code: %s" % proc.returncode)
            break

        if line:
            data = parse_rtl_power_line(line.strip())
            for freq, rssi in data['freq'].items():
                db.RFLog.add(data['datetime'], freq, rssi)
