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
            self._questions = []
            order = ["A", "B", "C", "D"]

            with open(self.csvpath) as csvfile:
                questionreader = DictReader(csvfile,
                    fieldnames=["question", "A", "B", "C", "D", "cat", "difficulty"],
                    delimiter=';')

                for question in questionreader:
                    random.shuffle(order)
                    self._questions.append({
                        "question": question["question"],
                        "A": question[order[0]],
                        "B": question[order[1]],
                        "C": question[order[2]],
                        "D": question[order[3]],
                        "correctAnswer": order.index("A")
                    })

        return self._questions

    def random(self):
        i = random.randrange(0, len(self._questions))
        return Question(self._questions[i], i)
