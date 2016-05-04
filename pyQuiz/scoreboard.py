import config

class Scoreboard:
    """Represents the scores of all participating quiz players."""

    def __init__(self, client):
        self._client = client
        self._scores = {
            self._client.ui.username: 0
        }

    def deltaUpdate(self, collectedAnswers, correctAnswer):
        """
        Updates the scoreboard, by increasing the score of the given users by 1

        collectedAnswers -- A dictionary with username => answerId
        correctAnswer -- Used to compare against the given dictonary. Users
            which answered accordingly get an additional point in the scoreboard
        """
        users = {u: a for u, a in collectedAnswers.items() if int(a) == int(correctAnswer)}
        for u in users:
            if u not in self._scores:
                self._scores[u] = 0

            self._scores[u] += 1

    def toDict(self):
        """
        Compatible representation of this object as dictonary.
        This representation should be used whenever the object is send over the
        wire via a umundo message.
        """
        return {
            'type': config.Message.SCORES,
            **self._scores,
        }

    def dispatchWelcome(self, msg):
        """
        Handles umundo 'welcome' messages.
        A new user is participating the quiz. Add him to the scoreboard.
        """
        username = msg.getMeta("username")

        if username not in self._scores:
            self._scores[username] = 0

    def dispatchScores(self, msg):
        """
        Handles umundo 'score' messages.
        Overrides the scoreboard, according to the given message
        """
        self._scores = dict((k, int(msg.getMeta(k))) for k in msg.getMetaKeys() if k != 'type' and not k.startswith('um.'))
        self._client.ui.updateScores(self._scores)
