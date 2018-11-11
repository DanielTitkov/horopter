import time
import json


def get_timestamps(delta=604800):
    to_ts = int(time.time())
    from_ts = to_ts - delta
    return from_ts, to_ts


def value_from_json(json_data, path=None, from_string=True):
    data = json.loads(json_data) if from_string else json_data
    for key in path.split('.'):
        result = data.get(key)
        data = result
    return result

