from typing import cast, Optional
import os
import dotenv
from dataclasses import dataclass
import dacite
import yaml

dotenv.load_dotenv()

@dataclass(frozen=True)
class AirsecConfig:
    timescaledb_username: str
    timescaledb_password: str
    timescaledb_dbname: str
    timescaledb_hostname: str = "localhost"
    timescaledb_port: int = 5432
    timescaledb_test_dbname: str = ""


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
    data = yaml.load(config_file)
    config  = dacite.from_dict(data_class=AirsecConfig, data=data['airsec'])
    return cast(AirsecConfig, config)


def load(config_file:Optional[str]=None) -> AirsecConfig:
    if config_file is not None:
        return load_config_from_file(config_file)

    return load_config_from_env()
