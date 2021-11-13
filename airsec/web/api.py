from dataclasses import dataclass
from typing import List
import json

from flask import (
    Flask,
    request,
    jsonify,
    render_template
)
from flask.json import _load_arg_defaults

from .. import (
    db,
    interfaces
)

from pathlib import Path
TEMPLATES = Path(__file__).parent / "templates"
STATICS = Path(__file__).parent / "static"

api = Flask("airsec",
            template_folder=TEMPLATES,
            static_folder=STATICS)

@api.before_first_request
def load():
    from ..applications import load_config
    db.init(load_config())
    db.setup_database()

@dataclass
class AllowListPayload:
    beacons: List[interfaces.AllowedBeacon]


@api.route("/api/v1/allowed-beacons", methods=["GET", "POST"])
def allow_list_route():
    if request.method == "POST":
        data = request.json
        if "beacons" not in data:
            return 422, "Missing required key `beacons`"

        beacons = data['beacons']
        if not isinstance(beacons, list):
            return 422, "`becacons` must be a list of becon properties to allow."

        beacons = list(map(lambda x: interfaces.AllowedBeacon(**x), beacons))
        bssids = [b.bssid for b in beacons]
        db.AllowedBeacons.add(bssids)

    beacons = db.AllowedBeacons.select()
    return jsonify(beacons=beacons,)

@api.route("/api/v1/traffic", methods=["GET"])
def traffic():
    latest = db.AppQueries.latest_beacons()
    beacons = [interfaces.BeaconPacketAPI.from_beacon_packet(bp) for bp in latest]
    return jsonify(count=len(beacons), beacons=beacons)


@api.route("/api/v1/rssi", methods=["GET"])
def beacon_rssi():
    bssid = request.args.get("bssid")
    query = f"WHERE bssid = '{bssid.upper()}' and time > now() - INTERVAL '1 year'"
    packets = db.BeaconPacket.select(filter=query)
    packets = [interfaces.BeaconPacketAPI.from_beacon_packet(bp) for bp in packets]
    return jsonify(data=packets, bssid=bssid)


@api.route("/")
def index_route():
    return render_template("index.html")