import config


class SpeechTest:

    def __init__(self):
        self.utterances = list()

    def add(self, utterance):
        self.utterances.append(utterance)

    def pop(self):
        return self.utterances.pop()

    def save(self, path):
        file = open(path, 'w')
        for utterance in self.utterances:
            file.write(config.get(config.RESULT_FORMAT).format(detected=utterance.word,
                                                               expected=utterance.expected,
                                                               confidence=utterance.confidence))
            file.write('\n')
        file.close()
