from contextlib import contextmanager
from datetime import datetime, timezone
import json
from typing import Union, Tuple

import psycopg2
from dateutil import tz

from . import config

TABLES = []

def register_table(cls):
    if not issubclass(cls, Table):
        raise TypeError("Registered tables must subclass Table")

    TABLES.append(cls)
    return cls

## TODO: Is there a better way to set the active database
## oether than setting up a global
ACTIVE_DB = None
def set_active_database(dbname: str):
    global ACTIVE_DB
    ACTIVE_DB = dbname


def get_connection_string(db_name=True) -> str:
    conf = config.load()
    if ACTIVE_DB is None:
        set_active_database(conf.timescaledb_dbname)

    conn_str = "postgres://{username}:{password}@{host}:{port}/{db}"

    return conn_str.format(
        username=conf.timescaledb_username,
        password=conf.timescaledb_password,
        host=conf.timescaledb_hostname,
        port=conf.timescaledb_port,
        db=ACTIVE_DB
    )


@contextmanager
def get_cursor():
    conn_str = get_connection_string()
    with psycopg2.connect(conn_str) as conn:
        cursor = conn.cursor()
        yield cursor
        cursor.close()


class Table:

    is_hypertable = False
    hypertable_field_name = 'time'

    @classmethod
    def create(cls):
        required_fields = ['name', 'fields']
        for field in required_fields:
            if not hasattr(cls, field) or not getattr(cls, field):
                raise ValueError("Cannot create table for %s. '%s' not defined." % (cls.__class__.__name__, field))

        with get_cursor() as cursor:
            field_strs = [" ".join(f) for f in cls.fields]

            sql = """
            CREATE TABLE IF NOT EXISTS {table_name} (
                {fields}
            );
            """.format(table_name=cls.name,
                       fields=",".join(field_strs)).strip().replace("\n", "")

            cursor.execute(sql)

            if cls.is_hypertable:
                sql = "SELECT create_hypertable('{table_name}', '{field}', if_not_exists => TRUE);".format(
                    table_name=cls.name,
                    field=cls.hypertable_field_name)
                cursor.execute(sql)


@register_table
class WifiPacket(Table):

    name = "wifi_packet"
    fields = (
        ("time", "TIMESTAMP WITHOUT TIME ZONE", "NOT NULL"),
        ("bssid", "MACADDR", "NOT NULL"),
        ("rssi", "INTEGER", "NOT NULL")
    )
    is_hypertable = True

    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    @classmethod
    def add(cls, dt: datetime, bssid: str, rssi: int):
        timestamp = dt.astimezone(timezone.utc).strftime(cls.date_format)
        values = f"('{timestamp}', '{bssid}', '{rssi}')"
        sql = f"INSERT INTO {cls.name} VALUES {values};"
        with get_cursor() as cursor:
            cursor.execute(sql)


    @classmethod
    def select(cls, filter=""):
        data = []
        column_names = [f[0] for f in cls.fields]
        sql = f"SELECT * FROM {cls.name} {filter}"
        with get_cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            for r in results:
                record = dict(zip(column_names, r))
                record['time'] = (record['time'].replace(tzinfo=tz.tzutc())
                                                .astimezone(tz.tzlocal())
                                                .replace(tzinfo=None))
                data.append(record)

        return data


@register_table
class WifiAllowList(Table):
    name = "wifi_allow_list"
    fields = (
        ("bssid", "MACADDR", "NOT NULL"),
    )

    @classmethod
    def add(cls, bssid: Union[str, list, Tuple]) -> None:
        if isinstance(bssid, str):
            bssid = (bssid,)

        sql = """
        INSERT INTO {name} (bssid)
        SELECT
            bssid
        FROM json_populate_recordset(null::{name}, %s);""".format(name=cls.name)

        values = [{"bssid": b} for b in bssid]
        with get_cursor() as cursor:
            cursor.execute(sql, (json.dumps(values), ))


    @classmethod
    def select(cls, filter=""):
        data = []
        column_names = [f[0] for f in cls.fields]
        columns = ",".join(column_names)

        sql = f"""
        SELECT {columns} FROM {cls.name} {filter}
        """

        with get_cursor() as cur:
            cur.execute(sql)
            results = cur.fetchall()
            for r in results:
                data.append(dict(zip(column_names, r)))

        return data


def setup_database() -> None:
    with get_cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;");

    for table in TABLES:
        table.create()


if __name__ == "__main__":
    setup_database()
