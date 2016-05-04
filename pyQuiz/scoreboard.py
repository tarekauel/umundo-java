class Scoreboard:
    def __init__(self, client):
        self._client = client
        self._scores = {
            self._client.ui.username: 0
        }

    def dispatchWelcome(self, msg):
        username = msg.getMeta("username")

        if username not in self._scores:
            self._scores[username] = 0

    def dispatchScores(self, msg):
        scores = dict((user, score) for (user, score) in msg.getMetaKeys() if user != 'type' and not user.startswith('um.'))
        print(scores)
        self._client.ui.updateScores(scores)
