import json
import struct
import wave

import vosk
from pvrecorder import PvRecorder

from utterance import Utterance


def get_recognizer(path):
    recognizer = vosk.KaldiRecognizer(vosk.Model(path), 16000)
    recognizer.SetWords(1)
    recognizer.SetPartialWords(1)

    return recognizer


def get_result(final_result):
    final_result_json = json.loads(final_result)
    if 'result' not in final_result_json:
        return Utterance(word='', confidence=1.0, full_text='')
    best_match = max(final_result_json['result'], key=lambda x: x['conf'])
    print(final_result_json)
    return Utterance(
        expected='',
        word=best_match['word'],
        confidence=best_match['conf'],
        full_text=final_result_json['text']
    )


class Recognizer:

    def __init__(self, audio_input_index, on_recognize, on_ready, threshold_ignore, save_recording):
        self.audio_input_index = audio_input_index
        self.on_recognize = on_recognize
        self.on_ready = on_ready
        self.threshold_ignore = threshold_ignore
        self.should_run = False
        self.save_recording = save_recording
        self.recording = []

    def start(self):
        self.recording = []
        self.should_run = True
        recorder = PvRecorder(device_index=self.audio_input_index, frame_length=512, buffer_size_msec=2000)
        recognizer = get_recognizer('model')

        recorder.start()

        self.on_ready()
        while self.should_run:
            frame = recorder.read()
            if self.save_recording:
                self.recording.extend(frame)
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

    def save_last_recording(self, path):
        with wave.open(path, 'w') as output:
            output.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            output.writeframes(struct.pack("h" * len(self.recording), *self.recording))
