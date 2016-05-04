import config

class Answer:
    def __init__(self, ui, question, answer_id):
        self._ui = ui
        self._q = question
        self._aid = answer_id

    def toDict(self):
        return {
            "type": config.Message.ANSWER,
            "username": self._ui.username,
            "questionId": self._q.getQuestionId(),
            "answer": self._aid,
        }

