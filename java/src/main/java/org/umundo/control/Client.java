package org.umundo.control;

import org.umundo.QuestionFactory;
import org.umundo.SimpleWebServer;
import org.umundo.WSServer;
import org.umundo.core.Discovery;
import org.umundo.core.Discovery.DiscoveryType;
import org.umundo.core.Message;
import org.umundo.core.Node;
import org.umundo.model.*;
import org.umundo.s11n.ITypedReceiver;
import org.umundo.s11n.TypedPublisher;
import org.umundo.s11n.TypedSubscriber;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;

public class Client {

  private Node gameNode;

  private long lastHeartbeat;
  private long priority = System.currentTimeMillis();

  private TypedSubscriber subscriber;
  private TypedPublisher publisher;

  private boolean leader = false;
  private WSServer wsServer;

  private int currentQuestionId = 0;
  private ArrayList<Question> questionHistory = new ArrayList<>();
  private final HashMap<String, Integer> scoreboard = new HashMap<>();

  private String username;
  private boolean run = true;

  private boolean electionGoesOn = true;

  public Client(int port, String username) {
    System.out.printf("Starting new client on port %d and %d, username: %s\n",
        port, port + 1, username);

    this.username = username;
    this.startUiServer(port);

    Discovery disc = new Discovery(DiscoveryType.MDNS);
    gameNode = new Node();
    disc.add(gameNode);

    // channel for sending and receiving questions
    String QUESTION_CHANNEL = "GAME_CHANNEL";
    subscriber = new TypedSubscriber(QUESTION_CHANNEL);
    subscriber.setReceiver(new Receiver(this));
    publisher = new TypedPublisher(QUESTION_CHANNEL);
    gameNode.addPublisher(publisher);
    gameNode.addSubscriber(subscriber);

    this.heartbeatSender();

    (new Thread() {
      @Override
      public void run() {
        while(true) {
          try {
            Thread.sleep(1000);
            int count = publisher.waitForSubscribers(0);
            System.out.println("Number of subscribers: " + count);
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
    }).start();
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
    while(this.run) {
      try {
        Thread.sleep(10000);

        if (this.leader) {
          // publish a new question if client is the leader
          Question q = QuestionFactory.getQuestion(++currentQuestionId);
          questionHistory.add(q);
          publisher.send(q.get());
          receivedQuestion(q);
        }
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
    System.exit(1);
    gameNode.removePublisher(publisher);
    gameNode.removeSubscriber(subscriber);
  }

  public void stop() {
    this.run = false;
  }

  private void receivedQuestion(Question q) {
    System.out.println("Received question with id " + q.getQuestionId());
    wsServer.sendQuestion(q);
  }

  public void answerFromUser(Answer answer) {
    System.out.println("Received answer from UI, question " + answer.getQuestionId());

    if (this.leader) {
      receivedAnswer(answer);
    } else {
      System.out.println("Send answer to leader");
      this.publisher.send(answer.get());
    }
  }

  private void heartbeatSender() {
    final Client client = this;
    client.lastHeartbeat = System.currentTimeMillis();
    (new Thread() {
      @Override
      public void run() {
        boolean run = true;
        while(run) {
          try {
            Thread.sleep(500);
            if (leader) {
              System.out.println("Leader sends heartbeat");
              publisher.send(new Heartbeat().get());
            } else {
              if (client.lastHeartbeat < System.currentTimeMillis() - 1000 * 5) {
                System.out.println("Detected no heartbeat for three seconds, start election.");
                // last heartbeat older than 3 secs, leader is considered to be down
                run = false;
                client.leaderElection();
              }
            }
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
        }
      }
    }).start();
  }

  private void leaderElection() {
    electionGoesOn = true;
    final Client client = this;
    (new Thread() {
      @Override
      public void run() {
        while (electionGoesOn) {
          try {
            Thread.sleep(250);
            publisher.send(new Priority(client.priority).get());
            System.out.println("Send my prio");
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
          client.leader = client.electionGoesOn;
          client.electionGoesOn = false;
          System.out.println("election finished and am I the leader: " + client.leader);
          client.heartbeatSender();
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
    }).start();
  }

  private void receivedPriority(Priority p) {
    if (p.getPriority() < this.priority) {
      System.out.println("Received a message from someone with a higher priority");
      // someone is active who will become the master
      electionGoesOn = false;
    }
  }

  private void receivedAnswer(Answer a) {
    if (this.leader) {
      System.out.printf("Received answer by %s for %d\n", a.getUsername(), a.getQuestionId());
      if (a.getQuestionId() == currentQuestionId) {
        // is latest question
        Question q = questionHistory.get(questionHistory.size() - 1);
        if (a.getAnswer() == q.getCorrectAnswer()) {
          System.out.printf("Answer by %s for %d was correct\n", a.getUsername(), a.getQuestionId());

          int lastScore = scoreboard.getOrDefault(a.getUsername(), 0);
          scoreboard.put(a.getUsername(), lastScore + 1);

          Scoreboard sb = new Scoreboard(scoreboard);
          publisher.send(sb.get());
          receivedScoreboard(sb);
        } else {
          System.out.printf("Answer by %s for %d was wrong\n", a.getUsername(), a.getQuestionId());
        }
      } else {
        // question is outdated
        System.out.printf("Answer by %s was too late\n", a.getUsername());
      }
    }
  }

  private void receivedHeartbeat(Heartbeat h) {
    System.out.println("received heartbeat");
    this.lastHeartbeat = h.getTimestamp();
    this.leader = false;
    this.electionGoesOn = false;
  }

  private void receivedScoreboard(Scoreboard scoreboard) {
    System.out.println("Received latest scoreboard");
    wsServer.sendScoreboard(scoreboard);
  }

  private static class Receiver implements ITypedReceiver {

    private Client client;

    private Receiver(Client client) {
      this.client = client;
    }

    public void receiveObject(Object o, Message message) {
      String type = message.getMeta("type");
      System.out.println("Received message of type " + type);
      switch (type) {
        case "question": client.receivedQuestion(Question.fromMessage(message)); break;
        case "answer": client.receivedAnswer(Answer.fromMessage(message)); break;
        case "score": client.receivedScoreboard(Scoreboard.fromMessage(message)); break;
        case "heartbeat": client.receivedHeartbeat(Heartbeat.fromMessage(message)); break;
        case "priority": client.receivedPriority(Priority.fromMessage(message)); break;
        default: System.err.println("Received unknown message type");
      }
    }
  }

  public String getUsername() {
    return username;
  }
}