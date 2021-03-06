from typing import cast, Optional
import os
import dotenv
from dataclasses import dataclass
import dacite
import yaml
from yaml import Loader

dotenv.load_dotenv()

@dataclass(frozen=True)
class AirsecConfig:
    # Required arguments
    timescaledb_username: str
    timescaledb_password: str
    timescaledb_dbname: str

    # SDR Configuration.
    sdr_lower_freq: str
    sdr_upper_freq: str
    sdr_bin_size: str

    # Optional values
    timescaledb_hostname: str = "localhost"
    timescaledb_port: int = 5432
    timescaledb_test_dbname: str = ""

    wlan_iface_name: str = ""

    sdr_integration_interval: Optional[int] = None
    sdr_tuner_gain: Optional[int] = None



def load_config_from_env() -> AirsecConfig:
    """
        Load the config file from environment variables.
    """

    env_mapping = {
        "timescaledb_username": ("TIMESCALEDB_USERNAME", str),
        "timescaledb_password": ("TIMESCALEDB_PASSWORD", str),
        "timescaledb_dbname": ("TIMESCALEDB_DBNAME", str),
        "timescaledb_hostname": ("TIMESCALEDB_HOSTNAME", str),
        "timescaledb_port": ("TIMESCALEDB_PORT", int),
        "timescaledb_test_dbname": ("TIMESCALEDB_TEST_DBNAME", str),
    }

    data = {}
    for key, (env_key, val_type) in env_mapping.items():
        value = os.getenv(env_key)
        if not value and not getattr(AirsecConfig, key):
            raise ValueError("Missing required environment variable: %s" % value)

        data[key] = val_type(value)

    return dacite.from_dict(data_class=AirsecConfig, data=data)


def load_config_from_file(config_file: str) -> AirsecConfig:
    with open(config_file) as file_:
        data = yaml.load(file_, Loader=Loader)

    config  = dacite.from_dict(data_class=AirsecConfig, data=data['airsec'])
    return cast(AirsecConfig, config)


def load(config_file:Optional[str]=None) -> AirsecConfig:
    if config_file is not None:
        return load_config_from_file(config_file)

    return load_config_from_env()
