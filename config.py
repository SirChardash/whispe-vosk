import json
from os.path import exists

config_location = 'config.json'
THEME = 'theme'
THRESHOLD_UNK = 'threshold_unk'
THRESHOLD_IGNORE = 'threshold_ignore'
RESULT_SAVE_DIR = 'result_save_dir'
SAVE_RECORDING = 'save_recording'
SHUFFLE_WORDS = 'shuffle_words'
MODEL_PATH = 'model_path'
AUDIO_INPUT = 'audio_input'
RESULT_FORMAT = 'result_format'

config = dict()

config_default = {
    THEME: 'light',
    THRESHOLD_UNK: 0.95,
    THRESHOLD_IGNORE: 0.8,
    RESULT_SAVE_DIR: '',
    SAVE_RECORDING: 0,
    SHUFFLE_WORDS: 0,
    MODEL_PATH: 'model',
    AUDIO_INPUT: '',
    RESULT_FORMAT: '{detected},{expected},{confidence}'
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
    if key in config:
        return config[key]
    elif key in config_default:
        put(key, config_default[key])
    return config[key]


def save():
    file = open('config.json', 'w')
    file.write(json.dumps(config, indent=2))
    file.close()
