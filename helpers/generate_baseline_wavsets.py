import os
import random
import re

import numpy

speakers = ['2', '6', '7', '8', '9', '14', '15', '16', '18', '19']
fake_names = ['tr1', 'tr2', 'tr3', 'tr4', 'tr5', 'tr6', 'tr7', 'tr8', 'tr9', 'vld']
home = '/home/chardash/Desktop/whispe_audio/heh/'
output_dir = '/home/chardash/Desktop/baseline/'


def create_dir(excluded):
    files = []
    for speaker in speakers:
        if speaker != excluded:
            files.extend(next(os.walk(home + speaker), (None, None, []))[2])
    random.shuffle(files)
    split = numpy.array_split(files, 10)
    speaker_output_dir = '%swhispe_audio_%s' % (output_dir, excluded)
    os.system('mkdir %s' % speaker_output_dir)
    for i in range(0, 10):
        os.system('mkdir %s/%s' % (speaker_output_dir, fake_names[i]))
        for filename in split[i]:
            original_speaker = re.sub('_.*$', '', re.sub('^.*?_', '', filename))
            source = '%s%s/%s' % (home, original_speaker, filename)
            dest = '%s/%s/%s' % (speaker_output_dir, fake_names[i], filename)
            os.system('ln %s %s' % (source, dest))


for test_speaker in speakers:
    create_dir(test_speaker)
