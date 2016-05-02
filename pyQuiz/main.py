import config
import umundo.umundo64 as umundo

from application import Application
from leader import Leader
from scoreboard import Scoreboard
from answer import Answer
from question import Question

class QuizGreeter(umundo.Greeter):
    def __init__(self, client):
        umundo.Greeter.__init__(self)
        self._client = client

    def welcome(self, pub, subStub):
        self._client.onSubscriber(pub, subStub)

    def farewell(self, pub, subStub):
        self._client.onSubscriberLeave(pub, subStub)

class QuizReceiver(umundo.Receiver):
    def __init__(self, client):
        umundo.Receiver.__init__(self)
        self._client = client

    def receive(self, msg):
        self._client.dispatch(msg)

class QuizClient():
    def __init__(self):
        self._initUmundo()
        self.ui = Application(self._onBtnPress, self._cleanup)
        self._leader = Leader(self)
        self._scoreboard = Scoreboard(self)

        # After(!) everything is initialized => register handlers
        self._publisher.setGreeter(self._greeter)
        self._subscriber.setReceiver(self._receiver)

    def _initUmundo(self):
        # Explicit references to umundo objects are required!
        self._greeter = QuizGreeter(self)
        self._receiver = QuizReceiver(self)

        self._publisher = umundo.Publisher(config.QUESTION_CHANNEL)
        self._subscriber = umundo.Subscriber(config.QUESTION_CHANNEL)

        self._node = umundo.Node()
        self._node.addPublisher(self._publisher)
        self._node.addSubscriber(self._subscriber)

        self._disc = umundo.Discovery(umundo.Discovery.MDNS)
        self._disc.add(self._node)

    def _cleanup(self):
        self._disc = None
        self._node = None
        self._subscriber = None
        self._publisher = None
        self._greeter = None
        self._receiver = None

    def _onBtnPress(self, btn):
        mapping = {
            Application.BTN_A: 0,
            Application.BTN_B: 1,
            Application.BTN_C: 2,
            Application.BTN_D: 3,
        }

        self.ui.highlightBtn(btn)

        if self._leader.isLeader():
            pass
        else:
            Answer(self, self._activeQuestion, mapping[btn]).send()

    def send(self, kvMap):
        print("Send message " + kvMap["type"])
        msg = umundo.Message()

        for k in kvMap:
            msg.putMeta(str(k), str(kvMap[k]))

        self._publisher.send(msg)

    def hasSubscribers(self):
        return self._publisher.waitForSubscribers(0) > 0

    def onSubscriber(self, pub, subStub):
        self.send({
            "type": config.Message.WELCOME,
            "username": self.ui.username,
        })

    def onSubscriberLeave(self, pub, subStub):
        pass

    def dispatch(self, msg):
        print ("Dispatch " + msg.getMeta("type"))

        mapping = {
            config.Message.HEARTBEAT: self._leader.dispatchHeartbeat,
            config.Message.PRIORITY: self._leader.dispatchPriority,
            config.Message.WELCOME: self._scoreboard.dispatchWelcome,
            config.Message.QUESTION: self.onQuestion,
            config.Message.ANSWER: self.onAnswer,
            config.Message.SCORES: self.onScores,
        }

        msgType = msg.getMeta("type")
        if msgType in mapping:
            mapping[msgType](msg)
        else:
            print("Unknown message type: ", msgType)

    def onQuestion(self, msg):
        self._activeQuestion = Question.fromMsg(msg)
        self.ui.updateQuestion(self._activeQuestion)

    def onAnswer(self, msg):
        pass

    def onScores(self, msg):
        pass

    def start(self):
        self.ui.schedule(500, self._leader.tick)
        self.ui.run()

client = QuizClient()
client.start()
