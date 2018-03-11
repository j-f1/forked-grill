import json

with open("config.json", "r") as config_file:
    for _k, _v in json.load(config_file).items():
        globals()[_k] = _v
