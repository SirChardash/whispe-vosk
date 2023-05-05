import json

from vosk import KaldiRecognizer, Model


def get_result(final_result):
    entry = json.loads(final_result)
    if 'result' in entry and entry['result'][0]['conf'] < 0.9:
        print('unconfident {0} for word {1}'.format(entry['result'][0]['conf'], entry['text']))
        return '<UNK>'
    return entry['text']


def get_whatever(final_result):
    entry = json.loads(final_result)
    return '{0} ({1})'.format(entry['text'], entry['result'][0]['conf'] if 'result' in entry else 1.0)


def get_recognizer(path):
    recognizer = KaldiRecognizer(Model(path), 16000)
    recognizer.SetWords(1)
    recognizer.SetPartialWords(1)

    return recognizer
