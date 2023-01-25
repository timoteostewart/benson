import pyttsx3
import re
import datetime
import my_time

# initialize and configure TTS processor
engine = pyttsx3.init()
# engine.setProperty(  # commented this out to be non-Windows friendly
#     "voice",
#     "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0",
# )


def get_spoken_title(domains, path_as_tokens):

    if not domains:
        return "(no domains)"

    if not path_as_tokens:
        return "(no path)"

    # first, try to extract any publication date data that may be in the path
    last_millennium = re.compile(r"\b1[89]\d\d\b")
    this_millennium = re.compile(r"\b20[012]\d\b")
    a_month = re.compile(r"\b\d\d?\b")
    a_day = re.compile(r"\b\d\d?\b")

    possible_pub_dates = []

    for i, v in enumerate(path_as_tokens):

        if this_millennium.match(v) or last_millennium.match(v):  # maybe a year
            candidate_pub_year = int(path_as_tokens[i])
            # look one ahead
            if (i + 1) < len(path_as_tokens) and a_month.match(path_as_tokens[i + 1]):
                candidate_pub_month = int(path_as_tokens[i + 1])  # maybe a month
                # look two ahead
                if (i + 2) < len(path_as_tokens) and a_day.match(path_as_tokens[i + 2]):
                    candidate_pub_day = int(
                        path_as_tokens[i + 2]
                    )  # maybe a month and a day
                else:
                    candidate_pub_day = None  # maybe a month, but not a day
            else:
                candidate_pub_month = None  # maybe a year, but not a month or a day
                candidate_pub_day = None
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

    # join the remaining path tokens to be our title
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
