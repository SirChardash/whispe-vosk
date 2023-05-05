import struct

from pvrecorder import PvRecorder

from util import get_whatever, get_recognizer

for index, device in enumerate(PvRecorder.get_audio_devices()):
    print(f"[{index}] {device}")

device_index = int(input('Select input: '))

recorder = PvRecorder(device_index=device_index, frame_length=512, buffer_size_msec=2000)
recognizer = get_recognizer('/home/chardash/model')

try:
    recorder.start()
    audio = []

    while True:
        frame = recorder.read()
        audio.extend(frame)
        if recognizer.AcceptWaveform(struct.pack("h" * len(frame), *frame)):
            print(get_whatever(recognizer.FinalResult()))
        if len(frame) == 0:
            break
except KeyboardInterrupt:
    recorder.stop()
finally:
    recorder.delete()
