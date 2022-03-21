import re
import yaml

import text_utils
import config



def trim_url(url):
    # remove scheme
    if url.startswith("http"):
        iodfs = url.index("//")
        url = url[(iodfs + 2) :]
    # remove "www[\d]?" subdomain
    if url.startswith("www."):
        url = url[4:]
    elif url.startswith("www") and url[3:4].isnumeric() and url[4:5] == ".":
        url = url[5:]
    # remove "en" subdomain
    if url.startswith("en."):
        url = url[3:]
    return url


def tokenize_url(url):
    url = trim_url(url)
    return text_utils.tokenize_string(url)


def get_domains(url: str):
    url = trim_url(url)

    try:  # remove path symbol (i.e., forward slash) and remainder of string
        iofs = url.index("/")
        url = url[:iofs]
    except:
        pass

    try:  # remove percent-encoded path symbol (i.e., forward slash) and remainder of string
        iofs = url.index("%2F")
        url = url[:iofs]
    except:
        pass

    try:  # remove query marker (i.e., question mark) and remainder of string
        ioqm = url.index("?")
        url = url[:ioqm]
    except:
        pass

    try:  # remove percent-encoded query marker (i.e., question mark) and remainder of string
        iofs = url.index("%3F")
        url = url[:iofs]
    except:
        pass

    try:  # remove port number symbol and remainder of string
        ioc = url.index(":")
        url = url[:ioc]
    except:
        pass

    domains = url
    return domains


def trim_path_tokens(path_as_tokens):
    # discard leading tokens likely to be irrelevant
    while path_as_tokens and path_as_tokens[0] in config.settings["IRRELEVANT_FIRST_TOKENS"]:
        path_as_tokens.pop(0)

    int_min5 = re.compile(r"\b\d{5,}\b")
    date_string = re.compile(r"\b20\d\d\d\d\d\d\b")

    int_4exact = re.compile(r"\b\d{4}\b")
    second_millennium = re.compile(r"\b1[0-9]\d\d\b")
    year_2000s_2010s = re.compile(r"\b20[01]\d\b")
    year_2020s = re.compile(r"\b202[012]\b")

    hex_string_min4 = re.compile(r"\b[a-f0-9]{4,}\b")
    all_digits = re.compile(r"\b\d+\b")
    all_letters = re.compile(r"\b[a-z]+\b")

    alphanumeric_str_min8 = re.compile(r"\b[a-z0-9]{8,}\b")

    # discard final tokens likely to be irrelevant
    while path_as_tokens and (
        (path_as_tokens[len(path_as_tokens) - 1] in config.settings["IRRELEVANT_LAST_TOKENS"])
        or (
            int_4exact.match(path_as_tokens[len(path_as_tokens) - 1])
            and not date_string.match(path_as_tokens[len(path_as_tokens) - 1])
            and not year_2020s.match(path_as_tokens[len(path_as_tokens) - 1])
            and not year_2000s_2010s.match(path_as_tokens[len(path_as_tokens) - 1])
            and not second_millennium.match(path_as_tokens[len(path_as_tokens) - 1])
        )
        or (
            int_min5.match(path_as_tokens[len(path_as_tokens) - 1])
            and not date_string.match(path_as_tokens[len(path_as_tokens) - 1])
        )
        or (
            hex_string_min4.match(path_as_tokens[len(path_as_tokens) - 1])
            and not all_digits.match(path_as_tokens[len(path_as_tokens) - 1])
            and not all_letters.match(path_as_tokens[len(path_as_tokens) - 1])
        )
        or (
            alphanumeric_str_min8.match(path_as_tokens[len(path_as_tokens) - 1])
            and not all_digits.match(path_as_tokens[len(path_as_tokens) - 1])
            and not all_letters.match(path_as_tokens[len(path_as_tokens) - 1])
        )
    ):
        # logger.info(f"deleting: {path_as_tokens[len(path_as_tokens) - 1]}")
        path_as_tokens.pop(len(path_as_tokens) - 1)

    new_path_as_tokens = []
    for token in path_as_tokens:
        if token not in config.settings["IRRELEVANT_TOKENS"]:
            new_path_as_tokens.append(token)

    if new_path_as_tokens:
        return new_path_as_tokens
    else:
        return []


def get_path_of_url(url, domains):
    iop = url.index(domains) + len(domains)
    path_as_str = url[iop:]
    if not path_as_str:
        return ""
    elif path_as_str.startswith("/"):
        return path_as_str[1:]
    else:
        return path_as_str
