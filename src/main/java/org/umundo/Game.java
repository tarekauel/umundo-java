package org.umundo;

import org.umundo.core.Discovery;
import org.umundo.core.Discovery.DiscoveryType;
import org.umundo.core.Message;
import org.umundo.core.Node;
import org.umundo.core.SubscriberStub;
import org.umundo.model.Answer;
import org.umundo.model.Question;
import org.umundo.model.Scoreboard;
import org.umundo.s11n.ITypedGreeter;
import org.umundo.s11n.ITypedReceiver;
import org.umundo.s11n.TypedPublisher;
import org.umundo.s11n.TypedSubscriber;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;

public class Game {

  private final String QUESTION_CHANNEL = "QUESTION_CHANNEL";
  private final String ANSWER_CHANNEL = "ANSWER_CHANNEL";
  private final String SCOREBOARD_CHANNEL = "SCOREBOARD_CHANNEL";

  private Discovery disc;
  private Node gameNode;

  private TypedSubscriber questionSub;
  private TypedPublisher questionPub;

  private TypedSubscriber answerSub;
  private TypedPublisher answerPub;

  private TypedSubscriber sbSub;
  private TypedPublisher sbPub;

  private boolean leader = false;
  private WSServer wsServer;

  private int currentQuestionId = 0;
  private ArrayList<Question> questionHistory = new ArrayList<>();
  private final HashMap<String, Integer> scoreboard = new HashMap<>();

  private String userName;

  private Game(int port, String userName) {
    (new Thread(){
      @Override
      public void run() {
        try {
          SimpleWebServer.main(port);
        } catch (Exception e) {
          e.printStackTrace();
        }
      }
    }).start();

    this.userName = userName;

    try {
      wsServer = new WSServer(this, port + 1);
      wsServer.start();
    } catch (UnknownHostException e) {
      e.printStackTrace();
      System.exit(1);
    }

    disc = new Discovery(DiscoveryType.MDNS);

    gameNode = new Node();
    disc.add(gameNode);

    leader = userName.equals("A");

    Receiver r = new Receiver(this);

    questionSub = new TypedSubscriber(QUESTION_CHANNEL, r);
    questionPub = new TypedPublisher(QUESTION_CHANNEL);

    if (leader) {
      answerSub = new TypedSubscriber(ANSWER_CHANNEL, r);
      gameNode.addSubscriber(answerSub);

      sbPub = new TypedPublisher(SCOREBOARD_CHANNEL);
      gameNode.addPublisher(sbPub);
    } else {
      sbSub = new TypedSubscriber(SCOREBOARD_CHANNEL, r);
      gameNode.addSubscriber(sbSub);

      answerPub = new TypedPublisher(ANSWER_CHANNEL);
      gameNode.addPublisher(answerPub);
    }

    gameNode.addPublisher(questionPub);
    gameNode.addSubscriber(questionSub);
  }

  public static void main(String[] args) throws Exception {
    int port = Integer.parseInt(args[0]);
    Game chat = new Game(port, args[1]);
    chat.run();
  }

  private void run() {
    boolean run = true;
    while(run) {
      try {
        Thread.sleep(10000);
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
      if (leader) {
        Question q = QuestionFactory.getQuestion(++currentQuestionId);
        questionHistory.add(q);
        questionPub.send(q.get());
        receivedQuestion(q);
      }
    }

    gameNode.removePublisher(questionPub);
    gameNode.removeSubscriber(questionSub);
  }

  private void receivedQuestion(Question q) {
    (new Thread() {
      @Override
      public void run() {
        wsServer.sendQuestion(q);
      }
    }).start();
  }

  public void answerFromUser(Answer answer) {
    System.err.println("Answer from user");

    if (leader) {
      receivedAnswer(answer);
    } else {
      answerPub.send(answer.get());
    }
  }

  private void receivedAnswer(Answer a) {
    if (a.getQuestionId() == currentQuestionId) {
      System.out.println("Received answer by " + a.getUsername());
      Question q = questionHistory.get(questionHistory.size() - 1);

      if (a.getAnswer() == q.getCorrectAnswer()) {
        System.out.println("Answer was correct");
        int lastScore = scoreboard.getOrDefault(a.getUsername(), 0);
        scoreboard.put(a.getUsername(), lastScore + 1);
        Scoreboard sb = new Scoreboard(scoreboard);
        sbPub.send(sb.get());
        receivedScoreboard(sb);
      } else {
        System.out.println("Answer was wrong");
      }
    } else {
      System.out.printf("Answer by %s was too late\n", a.getUsername());
    }
  }

  private void receivedScoreboard(Scoreboard scoreboard) {
    wsServer.sendScoreboard(scoreboard);
  }

  private static class Greeter implements ITypedGreeter {
    public void welcome(TypedPublisher typedPublisher, SubscriberStub subscriberStub) {

    }

    public void farewell(TypedPublisher typedPublisher, SubscriberStub subscriberStub) {

    }
  }

  private static class Receiver implements ITypedReceiver {

    private Game game;

    public Receiver(Game game) {
      this.game = game;
    }

    public void receiveObject(Object o, Message message) {
      String type = message.getMeta("type");
      switch (type) {
        case "question": game.receivedQuestion(Question.fromMessage(message)); break;
        case "answer": game.receivedAnswer(Answer.fromMessage(message)); break;
        case "score": game.receivedScoreboard(Scoreboard.fromMessage(message)); break;
      }
    }
  }

  public String getUserName() {
    return userName;
  }
}