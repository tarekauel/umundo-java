import config
import sys
import util

from questions import Questions

class Leader:
    """
    This class represents the quiz "leader". The leader is one priviliged client
    amongst all quiz players which is responsible for publishing new questions
    and calculate the score of the quiz players, based on their answers.
    """

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
            self._scoreboard.deltaUpdate(self._collectedAnswers, correctAnswer)
            self._collectedAnswers = {}

        self._client.send(self._scoreboard.toDict(), True)

    def _publishQuestion(self):
        q = self._questions.random()
        self._client.send(q.toDict(), True)
        self._lastQuestionSend = util.mtime()

    def isLeader(self):
        """
        Whether this client is currently the leader (which is responsible for
        score calculation and question publishing)
        """
        return self._lastHeartbeatSeen < util.mtime() - config.TAKEOVER_TIMEOUT_MS and \
            self._priority < self._minPrioritySeen

    def dispatchPriority(self, msg):
        """
        Gets called whenever a client is announcing his priority.
        This message is important during the leader election process.
        The client with the highest priority (=>lowest value) will take the leadership.
        """
        if not self.isLeader():
            self._minPrioritySeen = min(self._minPrioritySeen, int(msg.getMeta("priority")))

    def dispatchHeartbeat(self, msg):
        """
        Gets called whenever a heartbeat signal is received.
        A heartbeat signals the presence of a leader.
        """
        self._resetPriority()
        self._lastHeartbeatSeen = util.mtime()

    def dispatchAnswer(self, msg):
        """
        Gets called whenever an answer from a client received.
        If we are leader, we process the answer in order to calculate the scores.
        """
        if (not self.isLeader() or self._client.activeQuestion == None):
            return

        activeQuestionId = int(self._client.activeQuestion.getQuestionId())
        answerQuestionId = int(msg.getMeta("questionId"))

        if answerQuestionId == activeQuestionId:
            self._collectedAnswers[msg.getMeta("username")] = msg.getMeta("answer")

    def tick(self):
        """
        Gets called from the main event loop of tkinter.
        It basically takes care to perform the duty of the leader. If we are not
        the leader, there is not much work to be done here.
        """
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
