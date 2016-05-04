import config

class Scoreboard:
    def __init__(self, client):
        self._client = client
        self._scores = {
            self._client.ui.username: 0
        }

    def deltaUpdate(self, delta):
        for k in delta:
            if k not in self._scores:
                self._scores[k] = 0

            self._scores[k] += 1

    def toDict(self):
        return {
            'type': config.Message.SCORES,
            **self._scores,
        }

    def dispatchWelcome(self, msg):
        username = msg.getMeta("username")

        if username not in self._scores:
            self._scores[username] = 0

    def dispatchScores(self, msg):
        self._scores = dict((k, int(msg.getMeta(k))) for k in msg.getMetaKeys() if k != 'type' and not k.startswith('um.'))
        self._client.ui.updateScores(self._scores)
