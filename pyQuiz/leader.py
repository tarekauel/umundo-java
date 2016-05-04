import config
import sys
import util

from questions import Questions

class Leader:
    def __init__(self, client, scoreboard):
        self._client = client
        self._scoreboard = scoreboard
        self._questions = Questions()
        self._questions.load()

        self._collectedAnswers = {}
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

    def _processAnswers(self):
        if self._client.activeQuestion != None:
            correctAnswer = self._client.activeQuestion.getCorrectAnswer()
            correctAnswers = {k: v for k, v in self._collectedAnswers.items() if int(v) == int(correctAnswer)}
            self._scoreboard.deltaUpdate(correctAnswers)
            self._collectedAnswers = {}

        self._client.send(self._scoreboard.toDict(), True)

    def _publishQuestion(self):
        q = self._questions.random()
        self._client.send(q.toDict(), True)
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

    def dispatchAnswer(self, msg):
        if (not self.isLeader() or self._client.activeQuestion == None):
            return

        activeQuestionId = int(self._client.activeQuestion.getQuestionId())
        answerQuestionId = int(msg.getMeta("questionId"))

        if answerQuestionId == activeQuestionId:
                self._collectedAnswers[msg.getMeta("username")] = msg.getMeta("answer")

    def tick(self):
        if not self._client.hasSubscribers():
            self._lastHeartbeatSeen = util.mtime()
            self._resetPriority()
            return

        if self.isLeader():
            self._resetPriority()
            self._sendHeartbeat()

            if self._lastQuestionSend + config.QUESTION_TIME_MS < util.mtime():
                self._processAnswers()
                self._publishQuestion()
        elif self._lastHeartbeatSeen < util.mtime() - config.ELECTION_TIMEOUT_MS:
            self._sendPriority()
