import json
import os 
import base64
from datetime import date, datetime

from playhouse.shortcuts import model_to_dict, dict_to_model

def list_to_string(strings: list[str] | str | None, separator = "\n"):
    if type(strings) != list:
        return strings
    for i in range(len(strings)):
        strings[i] = str(strings[i])
    return separator.join(strings)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

def model_to_json(model):
    return json.dumps(model_to_dict(model), default = json_serial)

def concat_re_pattern(strings: list[str], reverse = False, ignoreCase = True):
    if not strings:
        return None
    pattern = ""
    if (reverse or ignoreCase):
        pattern += "(?"
    if (reverse):
        pattern += "r"
    if (ignoreCase):
        pattern += "i"
    if (reverse or ignoreCase):
        pattern += ")"
    for str in strings:
        pattern += f"({str})|"
    return pattern.rstrip("|")

def generate_base64_key(length = 32):
    key = os.urandom(length)
    base64_key = base64.b64encode(key).decode('utf-8')[:length]
    return base64_key
