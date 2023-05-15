import json
import struct

import vosk
from pvrecorder import PvRecorder

from spoken_word import SpokenWord


def get_recognizer(path):
    recognizer = vosk.KaldiRecognizer(vosk.Model(path), 16000)
    recognizer.SetWords(1)
    recognizer.SetPartialWords(1)

    return recognizer


def get_result(final_result):
    final_result_json = json.loads(final_result)
    if 'result' not in final_result_json:
        return SpokenWord(word='', confidence=1.0, full_text='')
    best_match = max(final_result_json['result'], key=lambda x: x['conf'])
    print(final_result_json)
    return SpokenWord(
        word=best_match['word'],
        confidence=best_match['conf'],
        full_text=final_result_json['text']
    )


class Recognizer:

    def __init__(self, audio_input_index, on_recognize, on_ready, threshold_ignore):
        self.audio_input_index = audio_input_index
        self.on_recognize = on_recognize
        self.on_ready = on_ready
        self.threshold_ignore = threshold_ignore
        self.should_run = False

    def start(self):
        self.should_run = True
        recorder = PvRecorder(device_index=self.audio_input_index, frame_length=512, buffer_size_msec=2000)
        recognizer = get_recognizer('model')

        recorder.start()

        self.on_ready()
        while self.should_run:
            frame = recorder.read()
            if recognizer.AcceptWaveform(struct.pack("h" * len(frame), *frame)):
                recognized = get_result(recognizer.FinalResult())
                if recognized.word != '':
                    if float(recognized.confidence) > self.threshold_ignore:
                        self.on_recognize(recognized)
                    else:
                        print('ignored ' + str(recognized))
            if len(frame) == 0:
                break

        recorder.stop()

    def stop(self):
        self.should_run = False
