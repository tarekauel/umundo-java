package org.umundo.model;

import org.umundo.core.Message;

public class Answer {

  private String username;
  private int answer;
  private int questionId;

  public Answer(String username, int answer, int questionId) {
    this.username = username;
    this.answer = answer;
    this.questionId = questionId;
  }

  public static Answer fromMessage(Message m) {
    return new Answer(
        m.getMeta("username"),
        Integer.parseInt(m.getMeta("answer")),
        Integer.parseInt(m.getMeta("questionId"))
    );
  }

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "answer");
    m.putMeta("username", username);
    m.putMeta("answer", answer + "");
    m.putMeta("questionId", questionId + "");
    return m;
  }

  public String getUsername() {
    return username;
  }

  public int getAnswer() {
    return answer;
  }

  public int getQuestionId() {
    return questionId;
  }
}
