class Scoreboard:
    def __init__(self, client):
        self._client = client
        self._scores = {
            self._client.ui.username: 0
        }

    def dispatchWelcome(self, msg):
        print("DEBUG_WELCOME_I")
        username = msg.getMeta("username")
        if username not in self._scores:
            self._scores[username] = 0
        print("DEBUG_WELCOME_II")
