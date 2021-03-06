package org.umundo.control;

import org.apache.log4j.Logger;
import org.umundo.QuestionFactory;
import org.umundo.SimpleWebServer;
import org.umundo.WSServer;
import org.umundo.core.Discovery;
import org.umundo.core.Discovery.DiscoveryType;
import org.umundo.core.Message;
import org.umundo.core.Node;
import org.umundo.core.SubscriberStub;
import org.umundo.model.*;
import org.umundo.s11n.ITypedGreeter;
import org.umundo.s11n.ITypedReceiver;
import org.umundo.s11n.TypedPublisher;
import org.umundo.s11n.TypedSubscriber;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;

public class Client {

  // log4j logger
  private static Logger log = Logger.getLogger(Client.class.getName());

  private Node gameNode;

  private long lastHeartbeat;
  private long priority = System.currentTimeMillis();

  private TypedSubscriber subscriber;
  private TypedPublisher publisher;

  // indicates if this node is the leader right now
  private boolean leader = false;

  // websocket server to communicate with the web ui
  private WSServer wsServer;

  private int currentQuestionId = 0;
  private ArrayList<Question> questionHistory = new ArrayList<>();
  // map of scores: (username, score)
  private HashMap<String, Integer> scoreboard = new HashMap<>();

  private String username;

  private boolean electionGoesOn = true;
  private Discovery disc;

  private final Client self = this;

  public Client(int port, String username) {
    log.info(String.format("Starting new client on port %d and %d, username: %s\n",
        port, port + 1, username));

    this.scoreboard.put(username, 0);

    this.username = username;
    this.startUiServer(port);

    disc = new Discovery(DiscoveryType.MDNS);
    gameNode = new Node();
    disc.add(gameNode);

    // channel for sending and receiving questions
    String QUESTION_CHANNEL = "GAME_CHANNEL";
    subscriber = new TypedSubscriber(QUESTION_CHANNEL);
    subscriber.setReceiver(new Receiver(this));
    publisher = new TypedPublisher(QUESTION_CHANNEL);
    publisher.setGreeter(new Greeter());
    gameNode.addPublisher(publisher);
    gameNode.addSubscriber(subscriber);

    this.checkSubscription();
    this.heartbeatSender();
  }

  private void checkSubscription() {
    (new Thread() {
      @Override
      public void run() {
        while(true) {
          try {
            Thread.sleep(1000);
            int count = publisher.waitForSubscribers(0);
            if (count == 0) {
              // due to some uMundo bug this is needed. This avoids that nodes loose the
              // connection to each other
              disc.remove(gameNode);
              Thread.sleep(100);
              disc.add(gameNode);
            }
            log.info("Number of subscribers: " + count);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
    }).start();
  }

  private void heartbeatSender() {
    // the leader sends a heartbeat to indicate that he is up.
    // non-leader node check if they have received a heartbeat within the last
    // five seconds, if not, the leader seems to be down and a leader election
    // has to start
    log.info("Heartbeat sender started");
    self.lastHeartbeat = System.currentTimeMillis();
    (new Thread() {
      @Override
      public void run() {
        boolean run = true;
        while(run) {
          try {
            Thread.sleep(2000);
            if (leader) {
              log.info("Leader sends heartbeat");
              publisher.send(new Heartbeat().get());
            } else {
              if (self.lastHeartbeat < System.currentTimeMillis() - 1000 * 5) {
                log.info("Detected no heartbeat for three seconds, start election.");
                // last heartbeat older than 5 secs, leader is considered to be down
                run = false;
                self.leaderElection();
              }
            }
            // send update info to client
            self.wsServer.sendIsLeader(leader);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
    }).start();
  }

  private void leaderElection() {
    // each client has a priority (starting time as long value). A smaller value
    // indicates a higher priority. If a message is received from a node with a
    // higher priority, this node can be sure, that the other one will become the
    // leader. If a node does not receive a message from a node with a higher priority
    // within 5 seconds, the node will become the new leader.
    electionGoesOn = true;
    (new Thread() {
      @Override
      public void run() {
        while (electionGoesOn) {
          try {
            Thread.sleep(250);
            publisher.send(new Priority(self.priority).get());
            log.info("Send my prio");

          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
    }).start();

    (new Thread() {
      @Override
      public void run() {
        try {
          Thread.sleep(5000);
          // if election still goes on --> this is the new leader
          self.leader = self.electionGoesOn;
          self.electionGoesOn = false;
          log.info("election finished and am I the leader: " + self.leader);
          self.heartbeatSender();
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
    }).start();
  }

  public String getUsername() {
    return username;
  }

  private void startUiServer(int port) {
    // Start a small web server that serves the ui
    (new Thread(){
      @Override
      public void run() {
        try {
          SimpleWebServer.start(port);
        } catch (Exception e) {
          System.err.println("Error while starting the ui server");
          e.printStackTrace();
          System.exit(1);
        }
      }
    }).start();

    // start the web socket server that is used to get the user inputs
    try {
      wsServer = new WSServer(this, port + 1);
      wsServer.start();
    } catch (UnknownHostException e) {
      System.err.println("Error while starting the web socket server");
      e.printStackTrace();
      System.exit(1);
    }
  }

  public void run() {
    while(true) {
      try {
        Thread.sleep(30000); // 30 seconds between two questions
        if (this.leader) {
          // if leader: send question
          // publish a new question if client is the leader
          Question q = QuestionFactory.getQuestion(++currentQuestionId);
          questionHistory.add(q);
          publisher.send(q.get());
          receivedQuestion(q);
          log.info("leader sent message");
        }
        log.info("question thread running");

      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
  }

  public void exit() {
    // method to kindly shutdown the node
    log.info("Going to quit");
    System.exit(0);
  }

  private void receivedQuestion(Question q) {
    // keep track of the question id in order to be able to take over as new leader without
    // confusing ids
    currentQuestionId = q.getQuestionId();
    questionHistory.add(q);
    log.info("Received question with id " + q.getQuestionId());
    wsServer.sendQuestion(q);
  }

  public void pullScoreboard() {
    // ui pulls the latest scoreboard if someone connects to the server
    wsServer.sendScoreboard(new Scoreboard(this.scoreboard));
  }

  public void answerFromUser(Answer answer) {
    log.info("Received answer from UI, question " + answer.getQuestionId());

    if (this.leader) {
      receivedAnswer(answer);
    } else {
      log.info("Send answer to leader");
      this.publisher.send(answer.get());
    }
  }

  private void sendWelcome() {
    Welcome w = new Welcome(this.getUsername());
    this.receivedWelcome(w);
    publisher.send(w.get());
  }

  private void receivedPriority(Priority p) {
    if (p.getPriority() < this.priority) {
      log.info("Received a message from someone with a higher priority");
      // someone is active who will become the master before this node will be the leader
      electionGoesOn = false;
    }
  }

  private void receivedAnswer(Answer a) {
    if (this.leader) {
      log.info(String.format("Received answer by %s for %d\n", a.getUsername(), a.getQuestionId()));
      if (a.getQuestionId() == currentQuestionId) {
        // is latest question
        Question q = questionHistory.get(questionHistory.size() - 1);
        if (a.getAnswer() == q.getCorrectAnswer()) {
          log.info(String.format("Answer by %s for %d was correct\n", a.getUsername(), a.getQuestionId()));

          //update scores
          int lastScore = scoreboard.getOrDefault(a.getUsername(), 0);
          scoreboard.put(a.getUsername(), lastScore + 1);

          Scoreboard sb = new Scoreboard(scoreboard);
          publisher.send(sb.get());
          receivedScoreboard(sb);
        } else {
          log.info(String.format("Answer by %s for %d was wrong\n", a.getUsername(), a.getQuestionId()));
        }
      } else {
        // question is outdated
        log.info(String.format("Answer by %s was too late\n", a.getUsername()));
      }
    }
  }

  private void receivedHeartbeat(Heartbeat h) {
    // if a node received a heartbeat it is not the leader.
    // corner case: two nodes think they are the leader. they will both deactivate each other
    // and elect a new leader following the protocol.
    log.info("received heartbeat");
    this.lastHeartbeat = h.getTimestamp();
    this.leader = false;
    this.electionGoesOn = false;
  }

  private void receivedScoreboard(Scoreboard scoreboard) {
    this.scoreboard = scoreboard.getScores();
    log.info("Received latest scoreboard");
    wsServer.sendScoreboard(scoreboard);
  }

  private void receivedWelcome(Welcome w) {
    this.scoreboard.put(w.getUsername(), this.scoreboard.getOrDefault(w.getUsername(), 0));
    this.receivedScoreboard(new Scoreboard(this.scoreboard));
  }

  private static class Receiver implements ITypedReceiver {

    private Client client;

    private Receiver(Client client) {
      this.client = client;
    }

    public void receiveObject(Object o, Message message) {
      // type determines the message type
      String type = message.getMeta("type");
      log.info("Received message of type " + type);
      switch (type) {
        case "question": client.receivedQuestion(Question.fromMessage(message)); break;
        case "answer": client.receivedAnswer(Answer.fromMessage(message)); break;
        case "score": client.receivedScoreboard(Scoreboard.fromMessage(message)); break;
        case "heartbeat": client.receivedHeartbeat(Heartbeat.fromMessage(message)); break;
        case "priority": client.receivedPriority(Priority.fromMessage(message)); break;
        case "welcome": client.receivedWelcome(Welcome.fromMessage(message)); break;
        default: log.error("Received unknown message type");
      }
    }
  }

  private class Greeter implements ITypedGreeter {
    @Override
    public void welcome(TypedPublisher typedPublisher, SubscriberStub subscriberStub) {
      self.sendWelcome();
    }

    @Override
    public void farewell(TypedPublisher typedPublisher, SubscriberStub subscriberStub) {
      // ignored, because users may rejoin
    }
  }
}