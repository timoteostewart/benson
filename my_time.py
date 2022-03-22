from time import time

import time
import datetime
import pytz


def get_time_now_in_seconds():
    return int(time.time())


def get_cur_datetime():
    dt_str = str(datetime.datetime.utcnow().replace(tzinfo=pytz.utc).isoformat())
    dt_str = dt_str[slice(0, dt_str.find("."))]
    dt_str += "Z"
    return dt_str


def get_sql_timestamp_now():
    sql_ts_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return sql_ts_str


def pretty_print_duration(num_seconds):
    num_seconds = int(num_seconds)
    
    m, s = divmod(num_seconds, 60)
    h, m = divmod(m, 60)
    if h == 0:
        slug = f"{m:02d}m:{s:02d}s"
    elif h < 10:
        slug = f"{h}h:{m:02d}m:{s:02d}s"
    elif h < 100:
        slug = f"{h:02d}h:{m:02d}m:{s:02d}s"
    else:
        slug = f"{h}h:{m:02d}m:{s:02d}s"

    return slug


def pretty_date(dt):
    dts = dt.strftime("%B %d, %Y")
    dts = dts.replace(" 0", " ")
    return dts
