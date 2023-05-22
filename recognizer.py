import json
import struct
import wave

import vosk
from pvrecorder import PvRecorder


class Utterance:

    def __init__(self, expected, word, confidence, full_text):
        self.expected = expected
        self.word = word
        self.confidence = confidence
        self.full_text = full_text

    def __str__(self):
        return '({0}, {1}, {2})'.format(self.word, self.confidence, self.full_text)


def get_recognizer(path):
    recognizer = vosk.KaldiRecognizer(vosk.Model(path), 16000)
    recognizer.SetWords(1)
    recognizer.SetPartialWords(1)

    return recognizer


def test_model(path):
    try:
        get_recognizer(path)
        return True
    except:
        return False


def get_result(final_result):
    final_result_json = json.loads(final_result)
    if 'result' not in final_result_json:
        return Utterance(word='', confidence=1.0, full_text='', expected=None)
    best_match = max(final_result_json['result'], key=lambda x: x['conf'])
    print(final_result_json)
    return Utterance(
        expected=None,
        word=best_match['word'],
        confidence=best_match['conf'],
        full_text=final_result_json['text']
    )


class Recognizer:

    def __init__(self, on_recognize, on_ready, threshold_ignore, save_recording, model_path, audio_input_index=None,
                 audio_stream=None):
        self.on_recognize = on_recognize
        self.on_ready = on_ready
        self.threshold_ignore = threshold_ignore
        self.should_run = False
        self.save_recording = save_recording
        self.model_path = model_path
        self.audio_input_index = audio_input_index
        self.audio_stream = audio_stream
        self.recording = []

    def start(self):
        self.recording = []
        self.should_run = True
        recognizer = get_recognizer(self.model_path)

        recorder = None
        if not self.audio_stream:
            recorder = PvRecorder(device_index=self.audio_input_index, frame_length=512, buffer_size_msec=2000)
            recorder.start()

        self.on_ready()
        while self.should_run:
            if self.audio_stream:
                frame = self.audio_stream.readframes(16000)
                frame = frame + (bytearray(32000 - len(frame)))
            else:
                read = recorder.read()
                if self.save_recording:
                    self.recording.extend(read)
                frame = struct.pack("h" * len(read), *read)

            if recognizer.AcceptWaveform(frame):
                recognized = get_result(recognizer.FinalResult())
                if recognized.word != '':
                    if float(recognized.confidence) > self.threshold_ignore:
                        self.on_recognize(recognized)
                    else:
                        print('ignored ' + str(recognized))
            if len(frame) == 0:
                break

        if not self.audio_stream:
            recorder.stop()

    def stop(self):
        self.should_run = False

    def save_last_recording(self, path):
        with wave.open(path, 'w') as output:
            output.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            output.writeframes(struct.pack("h" * len(self.recording), *self.recording))
