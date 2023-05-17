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
            file.write('{word},{expected},{confidence}\n'.format(word=utterance.word,
                                                                 expected=utterance.expected,
                                                                 confidence=utterance.confidence))
        file.close()
