import config
import sys
import util

from questions import Questions

class Leader:
    def __init__(self, client):
        self._client = client
        self._questions = Questions()
        self._questions.load()

        self._priority = util.mtime()
        self._lastHeartbeatSeen = util.mtime()
        self._minPrioritySeen = sys.maxsize
        self._lastQuestionSend = 0

    def _sendHeartbeat(self):
        self._client.send({
            "type": config.Message.HEARTBEAT,
        })

    def _sendPriority(self):
        self._client.send({
            "type": config.Message.PRIORITY,
            "priority": self._priority,
        })

    def _resetPriority(self):
        self._minPrioritySeen = sys.maxsize

    def _publishQuestion(self):
        if self._lastQuestionSend + config.QUESTION_TIME_MS < util.mtime():
            self._questions.random().publish(self._client)
            self._lastQuestionSend = util.mtime()

    def isLeader(self):
        return self._lastHeartbeatSeen < util.mtime() - config.TAKEOVER_TIMEOUT_MS and \
            self._priority < self._minPrioritySeen

    def dispatchPriority(self, msg):
        if not self.isLeader():
            self._minPrioritySeen = min(self._minPrioritySeen, int(msg.getMeta("priority")))

    def dispatchHeartbeat(self, msg):
        self._resetPriority()
        self._lastHeartbeatSeen = util.mtime()

    def tick(self):
        if not self._client.hasSubscribers():
            return

        if self.isLeader():
            self._resetPriority()
            self._sendHeartbeat()
            self._publishQuestion()
        elif self._lastHeartbeatSeen < util.mtime() - config.ELECTION_TIMEOUT_MS:
            self._sendPriority()

