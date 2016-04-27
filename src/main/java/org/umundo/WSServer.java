package org.umundo;

import com.google.gson.Gson;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;
import org.umundo.model.Answer;
import org.umundo.model.Question;
import org.umundo.model.Scoreboard;

import java.net.InetSocketAddress;
import java.net.UnknownHostException;

public class WSServer extends WebSocketServer {

  Game game;
  Gson gson = new Gson();

  WebSocket webSocket;

  public WSServer(Game game, int port) throws UnknownHostException {
    super(new InetSocketAddress(port));
    this.game = game;
    System.err.printf("Server created on port %d\n", port);
  }

  public void sendQuestion(Question q) {
    if (webSocket != null) {
      webSocket.send(gson.toJson(q));
      System.out.println("send question");
    }
  }

  public void sendScoreboard(Scoreboard sb) {
    if (webSocket != null) {
      webSocket.send(gson.toJson(sb));
    }
  }

  @Override
  public void onOpen(WebSocket webSocket, ClientHandshake clientHandshake) {
    System.err.println("Someone connected");
    webSocket.send("{\"username\": \"" + game.getUserName() + "\" }");
    this.webSocket = webSocket;
  }

  @Override
  public void onClose(WebSocket webSocket, int i, String s, boolean b) {

  }

  @Override
  public void onMessage(WebSocket webSocket, String s) {
    System.err.println("received answer: " + s);
    game.answerFromUser(gson.fromJson(s, Answer.class));
  }

  @Override
  public void onError(WebSocket webSocket, Exception e) {

  }
}
