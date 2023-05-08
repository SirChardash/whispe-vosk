import struct

import util
from pvrecorder import PvRecorder


class Recognizer:

    def __init__(self, audio_input_index, on_recognize):
        self.audio_input_index = audio_input_index
        self.on_recognize = on_recognize
        self.should_run = False

    def start(self):
        self.should_run = True
        recorder = PvRecorder(device_index=self.audio_input_index, frame_length=512, buffer_size_msec=2000)
        recognizer = util.get_recognizer('model')

        recorder.start()

        while self.should_run:
            frame = recorder.read()
            if recognizer.AcceptWaveform(struct.pack("h" * len(frame), *frame)):
                recognized = util.get_whatever(recognizer.FinalResult())
                if recognized != ' (1.0)':
                    self.on_recognize(recognized)
            if len(frame) == 0:
                break

        recorder.stop()

    def stop(self):
        self.should_run = False
