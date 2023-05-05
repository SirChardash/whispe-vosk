import os
import re
import time
import wave

from vosk import Model, KaldiRecognizer, SetLogLevel

from corpus import corpus
from util import get_result

SetLogLevel(-1)
home = '/home/chardash/Desktop/whispe_audio/heh/'

correctCount = 0
correctMapCount = {
    '1n.wav': 0,
    '2n.wav': 0,
    '3n.wav': 0,
    '4n.wav': 0,
    '5n.wav': 0
}
wrongCount = 0
# speakers = next(os.walk(home), (None, None, []))[1]
speakers = ['151', '152', '153', '154']

start = time.time()
for speaker in speakers:
    filenames = next(os.walk(home + speaker), (None, None, []))[2]
    for file in filenames:
        wf = wave.open(home + speaker + '/' + file, 'rb')

        model = Model('/home/chardash/model')
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(1)
        rec.SetPartialWords(1)

        res = []
        while True:
            data = wf.readframes(2000)
            if rec.AcceptWaveform(data):
                res.append(get_result(rec.FinalResult()))
            if len(data) == 0:
                break

        res.append(get_result(rec.FinalResult()))
        if '' in res:
            res.remove('')
        expected = corpus[re.sub('_.*', '', file)]

        if expected in res:
            correctCount = correctCount + 1
            correctMapCount[re.sub('.*_', '', file)] = correctMapCount[re.sub('.*_', '', file)] + 1
        else:
            wrongCount = wrongCount + 1

        print('[{0}] {1} -> {2}'.format('O' if expected in res else 'X', expected, res))

print('=================')
print('correct: {0}, wrong: {1}'.format(correctCount, wrongCount))
print(correctMapCount)
end = time.time()
print('took {0}s'.format(end - start))
