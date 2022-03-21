import ffmpeg
import argparse
import pyttsx3
import logging
import pathlib
import os
import re
import trafilatura
import datetime

import my_time
import db
import url_utils
import text_utils
import config


# keywords: content extraction, boilerplate removal

# setup logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler("benson_e.log", "a", "utf-8")
handler.setFormatter(
    logging.Formatter(
        f"%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


# other initial setup
required_directories = []
required_directories.append(config.settings["OUTPUT_DIR_TEXT_FILES"])
required_directories.append(config.settings["OUTPUT_DIR_MP3_FILES"])
for each_dir in required_directories:
    if not os.path.isdir(pathlib.Path(each_dir)):
        os.makedirs(pathlib.Path(each_dir))
        logger.warning(f"{each_dir} had to be created")


# initialize and configure TTS processor
engine = pyttsx3.init()
engine.setProperty(
    "voice",
    "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0",
)


def get_content(orig_url):  # uses trafilatura
    try:
        downloaded = trafilatura.fetch_url(orig_url)
    except Exception as e:
        print(f"trafilatura error while fetching url {orig_url}: {e}")
        return None

    try:
        result = trafilatura.extract(
            downloaded, include_comments=False
        )  # outputs main content and comments as plain text
    except Exception as e:
        print(f"trafilatura error extracting content from url {orig_url}: {e}")
        return None

    return result


def get_spoken_title(domains, path_as_tokens):

    if not domains:
        return "(no domains)"

    if not path_as_tokens:
        return "(no path)"

    last_millennium = re.compile(r"\b1[89]\d\d\b")
    this_millennium = re.compile(r"\b20[012]\d\b")
    a_month = re.compile(r"\b\d\d?\b")
    a_day = re.compile(r"\b\d\d?\b")

    possible_pub_dates = []

    for i, v in enumerate(path_as_tokens):
        if this_millennium.match(v) or last_millennium.match(v):
            candidate_pub_year = int(path_as_tokens[i])
            # look one ahead
            if (i + 1) < len(path_as_tokens) and a_month.match(path_as_tokens[i + 1]):
                candidate_pub_month = int(path_as_tokens[i + 1])
                # maybe a month and maybe a day
                if (i + 2) < len(path_as_tokens) and a_day.match(path_as_tokens[i + 2]):
                    candidate_pub_day = int(path_as_tokens[i + 2])
                else:
                    # maybe a month, but not a day
                    candidate_pub_day = None
                    pass
            else:
                # maybe a year, but not a month or a day
                candidate_pub_month = None
                candidate_pub_day = None
                pass
        else:
            candidate_pub_year = None

        if not candidate_pub_year:
            continue

        if candidate_pub_year > datetime.datetime.now().year:
            # publication year can't be in the future
            continue
        else:
            # we have a probable pub year!
            pass

        if candidate_pub_month and 1 <= candidate_pub_month <= 12:
            # we have a probable pub month!
            pass
        else:
            candidate_pub_month = None

        if candidate_pub_day and 1 <= candidate_pub_day <= 31:
            # we have a probable pub day!
            pass
        else:
            candidate_pub_day = None

        if not candidate_pub_month and not candidate_pub_day:
            pub_date_str = f"{candidate_pub_year}"
            possible_pub_dates.append((pub_date_str, i))
            continue

        if candidate_pub_month and not candidate_pub_day:
            months = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            pub_date_str = f"{months[candidate_pub_month - 1]} {candidate_pub_year}"

            possible_pub_dates.append((pub_date_str, i))
            continue

        dt = datetime.datetime(
            year=candidate_pub_year, month=candidate_pub_month, day=candidate_pub_day
        )

        pub_date_str = my_time.pretty_date(dt)
        possible_pub_dates.append((pub_date_str, i))
        continue

    if not possible_pub_dates:
        best_date = ""
    elif len(possible_pub_dates) == 1:
        best_date = possible_pub_dates[0][0]
        for _ in range(best_date.count(" ") + 1):
            path_as_tokens.pop(possible_pub_dates[0][1])
    else:  # pick the best: prefer the most components, and in case of tie, prefer the later date
        best_date = possible_pub_dates[0]
        for cur_date in possible_pub_dates:
            if cur_date[0].count(" ") > best_date[0].count(" "):
                best_date = cur_date
            elif cur_date[0].count(" ") == best_date[0].count(" "):
                if int(cur_date[0][-4:]) > int(best_date[0][-4:]):
                    best_date = cur_date
        for _ in range(best_date.count(" ") + 1):
            path_as_tokens.pop(possible_pub_dates[0][1])

    title_part = " ".join(path_as_tokens)
    if best_date:
        if best_date.count(" ") == 2:
            spoken_title = f"{title_part}, and it was published on {best_date}"
        else:
            spoken_title = f"{title_part}, and it was published in {best_date}"
    else:
        spoken_title = f"{title_part}"

    return spoken_title


def get_domains_pron(domains):
    domains_as_list = domains.split(".")
    domains_as_list[
        len(domains_as_list) - 1
    ] = f"dot {domains_as_list[len(domains_as_list) - 1]}"
    domains_pron = " ".join(domains_as_list)
    return domains_pron


if __name__ == "__main__":

    # setup parser and get command line arguments
    parser = argparse.ArgumentParser(
        description="Convert a list of URLs to their content as mp3s."
    )
    parser.add_argument(
        "--source",
        "-s",
        metavar="SOURCE",
        type=str,
        nargs=1,
        required=True,
        help="either a keyword or a filename",
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        metavar="N",
        type=int,
        nargs=1,
        required=False,
        help="where to put the mp3s",
    )
    parser.add_argument(
        "--domains_pron",
        "-dp",
        metavar="N",
        type=int,
        nargs=1,
        required=False,
        help="pronunciations of domain names",
    )

    args = parser.parse_args()
    source = args.source
    output_dir = args.output_dir
    domains_pron = args.domains_pron

    if output_dir:
        output_dir_str = str(output_dir[0])
        if not os.path.isdir(pathlib.Path(output_dir_str)):
            logger.error(f"directory {output_dir_str} not found! aborting")
            exit(1)
        else:
            output_dir = output_dir_str
    else:
        output_dir = config.settings["OUTPUT_DIR_MP3_FILES"]

    # initialize timing variables
    start_ts = my_time.get_time_now_in_seconds()
    start_dt = my_time.get_cur_datetime()

    # get list of URLs from source
    source_str = str(source[0])
    if source_str.lower() == "benson":
        link_entries = db.get_urls_from_benson()
    else:
        if os.path.exists(source_str):
            try:
                with open(source_str, "r", encoding="utf-8") as f:
                    list_of_urls = f.read().splitlines()
                    if not list_of_urls:
                        logger.error(f"file {source_str} is empty! aborting")
                        exit(1)
            except Exception as e:
                logger.error(f"error while reading {source_str}! aborting")
                exit(1)
            link_entries = []
            for each_url in list_of_urls:
                if not each_url:
                    continue
                link_entries.append(("", each_url, "", ""))
        else:
            logger.error(f"file {source_str} not found! aborting")
            exit(1)

    if not link_entries:
        logger.error(f"could not load any URLs! aborting")
        exit(1)

    # ingest pronunciations for domains
    domains_pronunciations = {}
    if domains_pron:
        domains_pron_str = str(domains_pron[0])
        if os.path.exists(domains_pron_str):
            try:
                with open(domains_pron_str) as f:
                    lines = f.read().splitlines()
            except Exception as e:
                logger.error(
                    f"could not read domains pronunciation file {domains_pron_str}! aborting"
                )
                exit(1)
            for ea_line in lines:
                fs = ea_line.index(" ")
                d = ea_line[:fs]
                p = ea_line[fs:].strip()
                domains_pronunciations[d] = p
        else:
            logger.error(
                f"domains pronunciation file {domains_pron_str} doesn't exist! aborting"
            )
            exit(1)
    else:  # try for default file
        if os.path.exists("domains_pronunciations.txt"):
            with open("domains_pronunciations.txt") as f:
                lines = f.read().splitlines()
            for ea_line in lines:
                fs = ea_line.index(" ")
                d = ea_line[:fs]
                p = ea_line[fs:].strip()
                domains_pronunciations[d] = p
        else:
            logger.info(f"no domains pronunciation file specified and no default found")

    # measure size of target dir, so we can measure the size of created mp3s
    pre_size_in_bytes = 0
    for f in os.scandir(output_dir):
        pre_size_in_bytes += os.path.getsize(f)
    mp3_count = 0
    mp3_duration_in_s = 0.0
    problem_count = 0

    for cur_link_entry in link_entries:

        # if mp3_count == 3:
        #     break

        if cur_link_entry[0]:
            row_id = int(cur_link_entry[0])
        else:
            row_id = 0

        orig_url = cur_link_entry[1]
        url = orig_url.lower()

        date_emailed = cur_link_entry[2]
        # date_loaded = cur_link_entry[3]

        domains = url_utils.get_domains(url)
        if domains in domains_pronunciations:
            domains_pron = domains_pronunciations[domains]
        else:
            domains_pron = get_domains_pron(domains)

        path = url_utils.get_path_of_url(url, domains)
        path_as_tokens = url_utils.trim_path_tokens(text_utils.tokenize_string(path))
        spoken_title = get_spoken_title(domains, path_as_tokens)

        if date_emailed:
            saved_via_email_slug = (
                f"It was saved via email on {my_time.pretty_date(date_emailed)}.\n\n"
            )
        else:
            saved_via_email_slug = ""

        intro_script = (
            f"The next article is from {domains_pron}.\n\n"
            f"Its title is {spoken_title}.\n\n"
            f"{saved_via_email_slug}"
            f"It was digitized to audio on {my_time.pretty_date(datetime.datetime.now())}.\n\n"
        )

        txt_filename = f"{text_utils.get_base_filename(url)}.txt"
        mp3_filename = f"{text_utils.get_base_filename(url)}.mp3"

        story_content = get_content(orig_url)

        if not story_content:
            error = f"error getting content from url {url}"
            logger.error(error)
            if row_id > 0:
                db.mark_row_as_egression_error_in_benson(
                    row_id, "error getting content from url"
                )  # no need to repeat URL in database
            problem_count += 1
            continue

        mp3_full_path = os.path.join(output_dir, mp3_filename)

        try:
            engine.save_to_file((intro_script + story_content), mp3_full_path)
            engine.runAndWait()
        except Exception as e:
            error = f"error while converting to mp3 file: {e}"
            logger.error(error)
            db.mark_row_as_egression_error_in_benson(error)
            problem_count += 1
            continue

        # presumably success by this point
        if row_id > 0:
            db.mark_row_as_egressed_in_benson(row_id)

        mp3_count += 1

        mp3_duration_in_s += float(
            ffmpeg.probe(os.path.join(output_dir, mp3_filename))[
                "format"
            ]["duration"]
        )

    # compute statistics
    end_ts = my_time.get_time_now_in_seconds()
    end_dt = my_time.get_cur_datetime()

    egression_duration_in_s = end_ts - start_ts

    post_size_in_bytes = 0
    for f in os.scandir(output_dir):
        post_size_in_bytes += os.path.getsize(f)

    size_delta_in_bytes = post_size_in_bytes - pre_size_in_bytes
    units = ["B", "KB", "MB", "GB"]
    unit_index = 0
    size_delta = size_delta_in_bytes
    while size_delta > 1_000:
        size_delta /= 1_000.0
        unit_index += 1

    # TODO: provide a dynamic "time taken and time left" progress indicator
    # TODO: if article isn't available, then try archive.is and Wayback Machine, check available snapshots starting with most recent
    # TODO: for domains not in a pronunciations file, check website and try to determine sayable name of website. check tags with keywords like title, by, byline, site, site_name, site-name, description, meta, etc. and compare strings with spaces to the closed-up strings in the domain name. e.g., avanwyk would be Andrich van Wyk

    print(
        "\nSummary:\n"
        f"source:        {source[0]}\n"
        f"start time:    {start_dt}\n"
        f"end time:      {end_dt}\n"
        f"time taken:    {my_time.pretty_print_duration(egression_duration_in_s)}\n"
        f"mp3s count:    {mp3_count - problem_count}\n"
        f"mp3s size:     {round(size_delta, 2)} {units[unit_index]}\n"
        f"mp3s duration: {my_time.pretty_print_duration(mp3_duration_in_s)}\n"
        f"mp3s dur/MB:   {my_time.pretty_print_duration(mp3_duration_in_s / (size_delta_in_bytes / 1_000_000))}\n"
        f"problem URLs:  {problem_count}\n"
    )
