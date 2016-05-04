import config

class Question:
    """Represents a multiple choice question."""

    def __init__(self, question, question_id):
        self._q = question
        self._qid = question_id

    def getQuestion(self):
        """String representation of the question"""
        return self._q["question"]

    def getQuestionId(self):
        """An identifier, unique to the localy loaded questions"""
        return self._qid

    def getAnswerA(self):
        """String representation of the first possible answer"""
        return self._q["A"]

    def getAnswerB(self):
        """String representation of the second possible answer"""
        return self._q["B"]

    def getAnswerC(self):
        """String representation of the third possible answer"""
        return self._q["C"]

    def getAnswerD(self):
        """String representation of the forth possible answer"""
        return self._q["D"]

    def getCorrectAnswer(self):
        """A number between 0-3 which identifies the correct answer to this question"""
        return self._q["correctAnswer"]

    def getTimeout(self):
        """The available time to answer this question in milliseconds"""
        return config.QUESTION_TIME_MS

    def toDict(self):
        """
        Compatible representation of this object as dictonary.
        This representation should be used whenever the object is send over the
        wire via a umundo message.
        """
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
        """
        Generates a question object from a umundo message.
        """
        return Question({
            "question": msg.getMeta("question"),
            "A": msg.getMeta("answerA"),
            "B": msg.getMeta("answerB"),
            "C": msg.getMeta("answerC"),
            "D": msg.getMeta("answerD"),
            "correctAnswer": msg.getMeta("correctAnswer"),
        }, msg.getMeta("id"))

