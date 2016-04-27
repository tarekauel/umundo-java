package org.umundo;

import org.umundo.model.Question;


public class QuestionFactory {

  public static Question getQuestion(int id) {
    return new Question(id, "Dumme Frage", "A", "B", "C", "D", 0);
  }
}
