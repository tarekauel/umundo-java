import config
import umundo.umundo64 as umundo

from application import Application

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
        umundo.Receiver.__init__(self)
        self._initUmundo()
        self.ui = Application(self._cleanup)

    def _initUmundo(self):
        # Explicit references to umundo objects are required!
        self._greeter = QuizGreeter(self)
        self._receiver = QuizReceiver(self)

        self._publisher = umundo.Publisher(config.QUESTION_CHANNEL)
        self._publisher.setGreeter(self._greeter)
        self._subscriber = umundo.Subscriber(config.QUESTION_CHANNEL)
        self._subscriber.setReceiver(self._receiver)

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

    def onSubscriber(self, pub, subStub):
        pass
        # print(subStub.getUUID())

    def onSubscriberLeave(self, pub, subStub):
        pass

    def dispatch(self, msg):
        mapping = {
            config.Message.HEARTBEAT : self.onHeartbeat,
            config.Message.QUESTION: self.onQuestion,
            config.Message.ANSWER: self.onAnswer,
            config.Message.NODE_ID: self.onNodeId,
            config.Message.SCORES: self.onScores,
        }

        msgType = msg.getMeta("type")
        if msgType in mapping:
            mapping[msgType](msg)
        else:
            print("Unknown message type: ", msgType)

    def onHeartbeat(self, msg):
        pass

    def onQuestion(self, msg):
        pass

    def onAnswer(self, msg):
        pass

    def onNodeId(self, msg):
        pass

    def onScores(self, msg):
        pass

    def heartbeat(self):
        msg = umundo.Message()
        msg.putMeta("type", config.Message.HEARTBEAT)
        msg.setData("ping")

        self._publisher.send(msg)
        print("o")
        print("Subscribers: ", self._publisher.waitForSubscribers(0))

    def start(self):
        self.ui.schedule(500, self.heartbeat)
        self.ui.run()

client = QuizClient()
client.start()

