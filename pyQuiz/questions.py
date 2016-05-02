import config
import random

from csv import DictReader
from question import Question

class Questions:
    def __init__(self, filename='assets/questions.csv'):
        self.csvpath = filename
        self._questions = None

    def load(self):
        if self._questions is None:
            with open(self.csvpath) as csvfile:
                questionreader = DictReader(csvfile,
                    fieldnames=["question", "A", "B", "C", "D", "cat", "correct"],
                    delimiter=';')
                self._questions = list(questionreader)

        return self._questions

    def random(self):
        i = random.randrange(0, len(self._questions))
        return Question(self._questions[i], i, config.QUESTION_TIME_MS)
