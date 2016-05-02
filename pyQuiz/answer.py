import config

class Answer:
    def __init__(self, client, question, answer_id):
        self._client = client
        self._q = question
        self._aid = answer_id

    def send(self):
        self._client.send({
            "type": config.Message.ANSWER,
            "username": self._client.ui.username,
            "questionId": self._q.getQuestionId(),
            "answer": self._aid,
        })
