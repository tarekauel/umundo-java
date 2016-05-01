package org.umundo.model;

import org.umundo.core.Message;

public class Welcome {

  private String username;

  public Welcome(String username) {
    this.username = username;
  }

  public String getUsername() {
    return username;
  }

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "welcome");
    m.putMeta("username", username);
    return m;
  }

  public static Welcome fromMessage(Message m) {
    return new Welcome(m.getMeta("username"));
  }
}
