import json
from os.path import exists

config_location = 'config.json'
THEME = 'theme'

config = {
    THEME: 'light'
}


def initialize():
    if not exists(config_location):
        save()
    global config
    file = open('config.json', 'r')
    config_from_file = json.loads(file.read())
    if config_from_file:
        config = config_from_file
    print(config)


def put(key, value):
    config[key] = value
    save()
    print(config)


def get(key):
    return config[key]


def save():
    file = open('config.json', 'w')
    file.write(json.dumps(config))
    file.close()
