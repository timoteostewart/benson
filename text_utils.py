import hashlib
import yaml

import url_utils
import config



def tokenize_string(string):
    tokens = []
    cur_token = ""

    for char in string:
        if char in config.settings["ALLOWED_AN_CHARS"]:
            cur_token += char
        else:
            if cur_token:
                tokens.append(cur_token)
                cur_token = ""
            else:
                pass
    if cur_token:
        tokens.append(cur_token)
    return tokens


def get_base_filename(url):
    tokens = url_utils.tokenize_url(url)
    md5 = hashlib.md5(url.encode("utf-8")).hexdigest()
    tokens.append(md5)
    base_filename = "-".join(tokens)
    return base_filename
