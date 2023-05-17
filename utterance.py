class Utterance:

    def __init__(self, expected, word, confidence, full_text):
        self.expected = expected
        self.word = word
        self.confidence = confidence
        self.full_text = full_text

    def __str__(self):
        return '({0}, {1}, {2})'.format(self.word, self.confidence, self.full_text)
