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
        """Gets called by umundo whenever a new subscriber is participating."""
        self._client.onSubscriber(pub, subStub)

    def farewell(self, pub, subStub):
        """Gets called by umundo whenever a node is leaving (or unsubscribes)."""
        self._client.onSubscriberLeave(pub, subStub)

class QuizReceiver(umundo.Receiver):
    def __init__(self, client):
        umundo.Receiver.__init__(self)
        self._client = client

    def receive(self, msg):
        """Gets called by umundo whenever a message to a subscribed channel is received."""
        self._client.dispatch(msg)

class QuizClient():
    """
    The client represents the application itself and controls the changes to the
    view, as propagated by the models.
    It also reacts to user events.
    """

    def __init__(self):
        self.ui = Application(self._onBtnPress, self._cleanup)
        self.activeQuestion = None
        self._answerLocked = True
        self._initUmundo()
        self._scoreboard = Scoreboard(self)
        self._leader = Leader(self, self._scoreboard)

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

    def _onBtnPress(self, pressedBtn):
        if self._answerLocked:
            return

        mapping = {
            Application.BTN_A: 0,
            Application.BTN_B: 1,
            Application.BTN_C: 2,
            Application.BTN_D: 3,
        }
        answer = Answer(self.ui, self.activeQuestion, mapping[pressedBtn])
        correctBtn = next(k for k,v in mapping.items() if v == int(self.activeQuestion.getCorrectAnswer()))

        self.ui.highlightBtn(correctBtn, None if pressedBtn == correctBtn else pressedBtn)
        self._answerLocked = True
        self.send(answer.toDict(), True)

    def _toMsg(self, kvMap):
        msg = umundo.Message()

        for k in kvMap:
            msg.putMeta(str(k), str(kvMap[k]))

        return msg

    def send(self, kvMap, dispatchToSelf=False):
        """
        Expects a dictonary which is then serialized and published as umundo message.

        kvMap -- The dictonary key-value pairs. Only string keys and string
            values are allowed. Each pair is attached as meta data to the message.
        dispatchToSelf -- Whether to simulate the receiving of the sent message.
        """
        # print("Send message " + kvMap["type"])
        message = self._toMsg(kvMap)
        self._publisher.send(message)

        if dispatchToSelf:
            self.dispatch(message)

    def hasSubscribers(self):
        """Whether there are any subscribers (players) besides ourselves."""
        return self._publisher.waitForSubscribers(0) > 0

    def onSubscriber(self, pub, subStub):
        """
        Gets called whenever a new player is participating.
        We respond via a welcome message to announce him our username.
        """
        self.send({
            "type": config.Message.WELCOME,
            "username": self.ui.username,
        })

    def onSubscriberLeave(self, pub, subStub):
        pass

    def onQuestion(self, msg):
        """
        Gets called when a new question is received.
        The received question is then displayed in the GUI.
        """
        self._answerLocked = False
        self.activeQuestion = Question.fromMsg(msg)
        self.ui.updateQuestion(self.activeQuestion)

    def dispatch(self, msg):
        """Delegate incoming messages to the appropriate handler functions"""
        # print ("Dispatch " + msg.getMeta("type"))

        mapping = {
            config.Message.HEARTBEAT: self._leader.dispatchHeartbeat,
            config.Message.PRIORITY: self._leader.dispatchPriority,
            config.Message.ANSWER: self._leader.dispatchAnswer,
            config.Message.WELCOME: self._scoreboard.dispatchWelcome,
            config.Message.SCORES: self._scoreboard.dispatchScores,
            config.Message.QUESTION: self.onQuestion,
        }

        msgType = msg.getMeta("type")
        if msgType in mapping:
            mapping[msgType](msg)
        else:
            print("Unknown message type: ", msgType)

    def start(self):
        """Starts the eventloop of the GUI"""
        self.ui.schedule(500, self._leader.tick)
        self.ui.run()

client = QuizClient()
client.start()
