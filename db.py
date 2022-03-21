import mysql.connector
import yaml

import my_time

with open("secrets.yaml", "r", encoding="utf-8") as f:
    secrets = yaml.safe_load(f)


def get_urls_from_benson():
    con = mysql.connector.connect(
        host=secrets["MYSQL"]["HOST"],
        database=secrets["MYSQL"]["DATABASE"],
        user=secrets["MYSQL"]["USER"],
        password=secrets["MYSQL"]["PASSWORD"],
    )
    cur = con.cursor()
    cur.execute(
        "SELECT * FROM urls WHERE date_egressed IS NULL AND egress_note IS NULL;"
    )
    link_entries = cur.fetchall()
    cur.close()
    con.close()

    return link_entries


def mark_row_as_egressed_in_benson(row_id: int):
    con = mysql.connector.connect(
        host=secrets["MYSQL"]["HOST"],
        database=secrets["MYSQL"]["DATABASE"],
        user=secrets["MYSQL"]["USER"],
        password=secrets["MYSQL"]["PASSWORD"],
    )
    cur = con.cursor()

    date_egressed = my_time.get_sql_timestamp_now()
    cur.execute(
        f"UPDATE urls SET date_egressed = '{date_egressed}' WHERE id = {row_id};"
    )
    con.commit()

    cur.close()
    con.close()


def mark_row_as_egression_error_in_benson(row_id: int, error_msg: str):
    con = mysql.connector.connect(
        host=secrets["MYSQL"]["HOST"],
        database=secrets["MYSQL"]["DATABASE"],
        user=secrets["MYSQL"]["USER"],
        password=secrets["MYSQL"]["PASSWORD"],
    )
    cur = con.cursor()

    cur.execute(f"UPDATE urls SET egress_note = '{error_msg}' WHERE id = {row_id};")
    con.commit()

    cur.close()
    con.close()
