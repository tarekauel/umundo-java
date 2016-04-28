package org.umundo.model;

import org.umundo.core.Message;

public class Priority {

  private long priority;

  public Priority(long priority) {
    this.priority = priority;
  }

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "priority");
    m.putMeta("priority", priority + "");
    return m;
  }

  public static Priority fromMessage(Message m) {
    return new Priority(Long.parseLong(m.getMeta("priority")));
  }

  public long getPriority() {
    return priority;
  }
}
