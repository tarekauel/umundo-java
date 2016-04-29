import umundo.umundo64 as umundo

from application import Application

class TestReceiver(umundo.Receiver):
    def __init__(self):
        super().__init__()

    def receive(self, *args):
        print("i")

testRcv = TestReceiver()

pub = umundo.Publisher("pingpong")
sub = umundo.Subscriber("pingpong")
sub.setReceiver(testRcv)

node = umundo.Node()
node.addPublisher(pub)
node.addSubscriber(sub)

disc = umundo.Discovery(0)
disc.add(node)

def ping():
    msg = umundo.Message()
    msg.setData("ping")
    pub.send(msg)

    print("o")

    app.master.after(1000, ping)

app = Application()
app.master.after(1000, ping)
app.run()

