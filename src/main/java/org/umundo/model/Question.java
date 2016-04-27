package org.umundo.model;

import org.umundo.core.Message;

public class Question {

  private int questionId;
  private String question;
  private String answerA;
  private String answerB;
  private String answerC;
  private String answerD;
  private int correctAnswer;

  public Question(int questionId, String question, String answerA, String answerB, String answerC, String answerD, int correctAnswer) {
    this.questionId = questionId;
    this.question = question;
    this.answerA = answerA;
    this.answerB = answerB;
    this.answerC = answerC;
    this.answerD = answerD;
    this.correctAnswer = correctAnswer;
  }

  public static Question fromMessage(Message m) {
    return new Question(
        Integer.parseInt(m.getMeta("id")),
        m.getMeta("question"),
        m.getMeta("answerA"),
        m.getMeta("answerB"),
        m.getMeta("answerC"),
        m.getMeta("answerD"),
        Integer.parseInt(m.getMeta("correctAnswer"))
    );
  };

  public Message get() {
    Message m = new Message();
    m.putMeta("type", "question");
    m.putMeta("id", questionId + "");
    m.putMeta("question", question);
    m.putMeta("answerA", answerA);
    m.putMeta("answerB", answerB);
    m.putMeta("answerC", answerC);
    m.putMeta("answerD", answerD);
    m.putMeta("correctAnswer", correctAnswer + "");
    return m;
  }

  public int getQuestionId() {
    return questionId;
  }

  public String getQuestion() {
    return question;
  }

  public String getAnswerA() {
    return answerA;
  }

  public String getAnswerB() {
    return answerB;
  }

  public String getAnswerC() {
    return answerC;
  }

  public String getAnswerD() {
    return answerD;
  }

  public int getCorrectAnswer() {
    return correctAnswer;
  }
}
