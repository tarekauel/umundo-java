package org.umundo;


import org.apache.log4j.Logger;
import org.umundo.control.Client;

public class Game {

  private static Logger log = Logger.getLogger(Game.class.getName());

  public static void main(String[] args) throws Exception {
    int port;
    try {
      port = Integer.parseInt(args[0]);
    } catch (NumberFormatException e) {
      log.error("Error while parsing input port:" + e);
      System.exit(1);
      return;
    }
    new Client(port, args[1]).run();
  }
}
