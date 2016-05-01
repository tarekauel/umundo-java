import config

class Question:
    def __init__(self, question, question_id, timeout):
        self._q = question
        self._qid = question_id
        self._t = timeout

    def publish(self, client):
        client.send({
            "type": config.Message.QUESTION,
            "id": self._qid,
            "question": self._q["question"],
            "answerA": self._q["A"],
            "answerB": self._q["B"],
            "answerC": self._q["C"],
            "answerD": self._q["D"],
            "correctAnswer": 1, # for compatibility,
            "timeout": self._t,
        })
        client.ui.updateQuestion(self)

    def getQuestion(self):
        return self._q["question"]

    def getAnswerA(self):
        return self._q["A"]

    def getAnswerB(self):
        return self._q["B"]

    def getAnswerC(self):
        return self._q["C"]

    def getAnswerD(self):
        return self._q["D"]

    def getTimeout(self):
        return self._t

    def fromMsg(msg):
        return Question({
            "question": msg.getMeta("question"),
            "A": msg.getMeta("answerA"),
            "B": msg.getMeta("answerB"),
            "C": msg.getMeta("answerC"),
            "D": msg.getMeta("answerD"),
        }, msg.getMeta("id"), msg.getMeta("timeout"))

