package org.umundo.model;

import org.umundo.core.Message;

import java.util.HashMap;
import java.util.Map;

public class Scoreboard {

  private HashMap<String, Integer> scores;

  public Scoreboard(HashMap<String, Integer> scores) {
    this.scores = scores;
  }

  public HashMap<String, Integer> getScores() {
    return scores;
  }

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "score");
    for(Map.Entry<String, Integer> e : scores.entrySet()) {
      m.putMeta(e.getKey(), e.getValue().toString());
    }
    return m;
  }

  public static Scoreboard fromMessage(Message m) {
    HashMap<String, Integer> scores = new HashMap<>();
    for(int i =0; i < m.getMetaKeys().size(); i++) {
      String key = m.getMetaKeys().get(i);
      if (!key.equals("type") && !key.startsWith("um.")) {
        scores.put(key, Integer.parseInt(m.getMeta(key)));
      }
    }
    return new Scoreboard(scores);
  }
}
