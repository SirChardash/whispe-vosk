class SpokenWord:

    def __init__(self, word, confidence, full_text):
        self.word = word
        self.confidence = confidence
        self.full_text = full_text

    def __str__(self):
        return '({0}, {1}, {2})'.format(self.word, self.confidence, self.full_text)
