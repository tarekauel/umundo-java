class Scoreboard:
    def __init__(self, client):
        self._client = client
        self._scores = {
            self._client.ui.username: 0
        }

    def dispatchWelcome(self, msg):
        print("DEBUG_WELCOME_I")
        username = msg.getMeta("username")
        print("DEBUG_WELCOME_II")
        if username not in self._scores:
            print("DEBUG_WELCOME_III")
            self._scores[username] = 0
            print("DEBUG_WELCOME_VI")
        print("DEBUG_WELCOME_V")
