import os
import re
import wave

from vosk import Model, KaldiRecognizer

from helpers.corpus import corpus
from util import get_result


def test(home, model_path, speakers):
    if not os.path.exists(model_path):
        return None
    correct_count = 0
    wrong_count = 0
    for speaker in speakers:
        filenames = next(os.walk(home + speaker), (None, None, []))[2]
        model = Model(model_path)
        for file in filenames:
            wf = wave.open(home + speaker + '/' + file, 'rb')
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

            print('%s -? %s' % (expected, res))
            if expected in res:
                correct_count = correct_count + 1
                # correctMapCount[re.sub('.*_', '', file)] = correctMapCount[re.sub('.*_', '', file)] + 1
            else:
                wrong_count = wrong_count + 1
        return correct_count / (correct_count + wrong_count)


audio_home = '/home/chardash/Desktop/whispe_audio/heh/'
model_path_template = '/home/chardash/baseline_models/%s/model'
original_speakers = ['2', '6', '7', '8', '9', '14', '15', '16', '18', '19']
grades = []
for speaker_id in original_speakers:
    grades.append(test(audio_home, model_path_template % speaker_id, [speaker_id]))

print(grades)
