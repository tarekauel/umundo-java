import config

class Question:
    def __init__(self, question, question_id):
        self._q = question
        self._qid = question_id

    def getQuestion(self):
        return self._q["question"]

    def getQuestionId(self):
        return self._qid

    def getAnswerA(self):
        return self._q["A"]

    def getAnswerB(self):
        return self._q["B"]

    def getAnswerC(self):
        return self._q["C"]

    def getAnswerD(self):
        return self._q["D"]

    def getCorrectAnswer(self):
        return self._q["correctAnswer"]

    def getTimeout(self):
        return config.QUESTION_TIME_MS

    def toDict(self):
        return {
            "type": config.Message.QUESTION,
            "id": self._qid,
            "question": self._q["question"],
            "answerA": self._q["A"],
            "answerB": self._q["B"],
            "answerC": self._q["C"],
            "answerD": self._q["D"],
            "correctAnswer": self._q["correctAnswer"],
            "timeout": config.QUESTION_TIME_MS,
        }

    def fromMsg(msg):
        return Question({
            "question": msg.getMeta("question"),
            "A": msg.getMeta("answerA"),
            "B": msg.getMeta("answerB"),
            "C": msg.getMeta("answerC"),
            "D": msg.getMeta("answerD"),
            "correctAnswer": msg.getMeta("correctAnswer"),
        }, msg.getMeta("id"))

