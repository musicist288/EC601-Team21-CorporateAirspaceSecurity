from typing import Optional
from pathlib import Path
from .. import config

LOCAL_CONFIG_FILES = [
    Path("~/.local/etc/airsec/airsec.conf.yaml").expanduser(),
    Path("/etc/airsec/airsec.conf.yaml")
]

def load_config() -> Optional[config.AirsecConfig]:
    for path in LOCAL_CONFIG_FILES:
        if path.exists():
            return config.load_config_from_file(str(path))
