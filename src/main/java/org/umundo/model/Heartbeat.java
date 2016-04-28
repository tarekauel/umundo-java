package org.umundo.model;

import org.umundo.core.Message;

public class Heartbeat {

  private long timestamp = System.currentTimeMillis();

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "heartbeat");
    return m;
  }

  public long getTimestamp() {
    return timestamp;
  }

  public static Heartbeat fromMessage(Message m) {
    return new Heartbeat();
  }
}
