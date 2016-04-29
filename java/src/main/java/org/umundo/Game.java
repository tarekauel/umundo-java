package org.umundo;


import org.umundo.control.Client;

public class Game {

  public static void main(String[] args) throws Exception {
    int port;
    try {
      port = Integer.parseInt(args[0]);
    } catch (NumberFormatException e) {
      System.err.println("Error while parsing input port:" + e);
      System.exit(1);
      return;
    }
    new Client(port, args[1]).run();
  }
}
