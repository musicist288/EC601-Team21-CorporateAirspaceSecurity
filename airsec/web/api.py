from dataclasses import dataclass
from typing import List
import json

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    make_response
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
            return make_response("Missing required key `beacons`", 422)

        beacons = data['beacons']
        if not isinstance(beacons, list):
            return make_response("`becacons` must be a list of becon properties to allow.", 422)

        beacons = list(map(lambda x: interfaces.AllowedBeacon(**x), beacons))
        bssids = [b.bssid for b in beacons]
        db.AllowedBeacons.add(bssids)

    beacons = db.AllowedBeacons.select()
    return jsonify(beacons=beacons,)


@api.route("/api/v1/traffic", methods=["GET"])
def traffic():
    latest = db.AppQueries.latest_beacons()
    beacons = [interfaces.BeaconPacketAPI.from_beacon_packet(bp) for bp in latest]
    beacons = [b.to_dict() for b in beacons]
    return jsonify(count=len(beacons), beacons=beacons)

@api.route("/api/v1/evil-twins", methods=["GET"])
def evil_twins():
    latest = db.AppQueries.evil_twins()
    beacons = [interfaces.BeaconPacketAPI.from_beacon_packet(bp) for bp in latest]
    beacons = [b.to_dict() for b in beacons]
    return jsonify(count=len(beacons), beacons=beacons)


@api.route("/api/v1/rssi", methods=["GET"])
def beacon_rssi():
    bssids = request.args.to_dict(flat=False).get("bssid")
    if not bssids:
        return make_response("Must specify at least one bssid", 422)

    if isinstance(bssids, str):
        bssids = [bssids]
    data = {}
    for bssid in bssids:
        query = f"WHERE bssid = %s and time > now() - INTERVAL '1 year'"
        results = db.BeaconPacket.select(filter=query, values=(bssid,))
        packets = [interfaces.BeaconPacketAPI.from_beacon_packet(bp) for bp in results]
        packets = [p.to_dict() for p in packets]
        data[bssid] = packets
    return jsonify(data)


@api.route("/")
def index_route():
    return render_template("index.html")