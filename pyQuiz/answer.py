import config

class Answer:
    """Represents the answer to a quiz question."""

    def __init__(self, ui, question, answer_id):
        self._ui = ui
        self._q = question
        self._aid = answer_id

    def toDict(self):
        """
        Compatible representation of this object as dictonary.
        This representation should be used whenever the object is send over the
        wire via a umundo message.
        """
        return {
            "type": config.Message.ANSWER,
            "username": self._ui.username,
            "questionId": self._q.getQuestionId(),
            "answer": self._aid,
        }

