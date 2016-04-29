package org.umundo;

import org.umundo.model.Question;

import java.util.Random;


public class QuestionFactory {

  private static final String[] questions = new String[] {
      "How many people live in Mannheim?;200k;250k;300k;350k;2",
      "Who invented the concept for relational databases?;Codd;Brin;Watson;Miller;0",
      "Which operating system is based on a UNIX kernel?;Linux;Win NT;OS X;DOS;2",
      "Which layer does not exist in the ISO/OSI Model?;Application;Session;Transport;Authentication;3"
  };

  private static Random r = new Random();

  public static Question getQuestion(int id) {
    String[] parts = questions[r.nextInt(questions.length)].split(";");
    return new Question(id, parts[0], parts[1], parts[2], parts[3], parts[4],
        Integer.parseInt(parts[5]));

  }
}
