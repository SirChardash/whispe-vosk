import wave

from recognizer import get_result, get_recognizer

wf = wave.open('/home/chardash/heh3.wav')
rec = get_recognizer('/home/chardash/model')

res = []
while True:
    data = wf.readframes(2000)
    if rec.AcceptWaveform(data):
        res.append(get_result(rec.FinalResult()))

    if len(data) == 0:
        break

res.append(get_result(rec.FinalResult()))

print(res)
