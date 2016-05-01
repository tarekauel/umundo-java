package org.umundo;

import com.google.gson.Gson;
import org.java_websocket.WebSocket;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;
import org.umundo.control.Client;
import org.umundo.model.Answer;
import org.umundo.model.Question;
import org.umundo.model.Scoreboard;

import java.net.InetSocketAddress;
import java.net.UnknownHostException;

public class WSServer extends WebSocketServer {

  private Client client;
  private Gson gson = new Gson();

  private WebSocket webSocket;

  public WSServer(Client client, int port) throws UnknownHostException {
    super(new InetSocketAddress(port));
    this.client = client;
    System.out.printf("Server created on port %d\n", port);
  }

  public void sendQuestion(Question q) {
    // check whether someone connected already, else just ignore the question
    if (webSocket != null) {
      webSocket.send(gson.toJson(q));
      System.out.println("send question");
    }
  }

  public void sendScoreboard(Scoreboard sb) {
    // check is a client is already active
    if (webSocket != null) {
      webSocket.send(gson.toJson(sb));
    }
  }

  public void sendIsLeader(boolean isLeader) {
    if (webSocket != null) {
      webSocket.send("{\"leader\": " +  isLeader + "}");
    }
  }

  @Override
  public void onOpen(WebSocket webSocket, ClientHandshake clientHandshake) {
    System.out.println("Someone connected");
    webSocket.send("{\"username\": \"" + client.getUsername() + "\" }");
    this.webSocket = webSocket;
  }

  @Override
  public void onClose(WebSocket webSocket, int i, String s, boolean b) {
    if (this.webSocket == webSocket) {
      // user closed the browser tab
      this.webSocket = null;
    }
  }

  @Override
  public void onMessage(WebSocket webSocket, String s) {
    System.out.println("received message from ui: " + s);
    client.answerFromUser(gson.fromJson(s, Answer.class));
  }

  @Override
  public void onError(WebSocket webSocket, Exception e) {

  }
}
