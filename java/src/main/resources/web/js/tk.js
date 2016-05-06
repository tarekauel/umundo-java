var timeToAnswer = 0;
var questionId = 0;
var correctAnswer = 0;
var lastSendId = 0;
var connection = new WebSocket('ws://' + location.hostname + ':' + (parseInt(location.port) + 1));
var username = "";

connection.onopen = function() {
  console.log('connection established');
}

connection.onclose = function() {
  console.log('connection closed');
}

connection.onerror = function(error) {
  console.log('an error occurred');
}

connection.onmessage = function(msg) {
  var json = JSON.parse(msg.data);
  console.log("received message:")
  console.log(json);
  if (typeof json.username === 'string') {
    console.log("seems to be welcome message")
    username = json.username;
  } else if (typeof json.question === 'string') {
    console.log("seems to be a question");
    document.getElementById('question').innerHTML = json.question;
    document.getElementById('A').innerHTML = json.answerA;
    document.getElementById('B').innerHTML = json.answerB;
    document.getElementById('C').innerHTML = json.answerC;
    document.getElementById('D').innerHTML = json.answerD;
    document.getElementById('A').className = "btn btn-default";
    document.getElementById('B').className = "btn btn-default";
    document.getElementById('C').className = "btn btn-default";
    document.getElementById('D').className = "btn btn-default";
    questionId = json.questionId;
    correctAnswer = json.correctAnswer;
    timeToAnswer = 300;
  } else if (typeof json.leader === 'boolean') {
    console.log("seems to be a leader information")
    if (json.leader) {
      document.getElementById("leader").innerHTML = "Leader: Yes";
    } else {
      document.getElementById("leader").innerHTML =  "Leader: No";
    }
  } else if (typeof json.scores === 'object') {
    console.log("seems to be a scores message");
    var scores = [];
    Object.keys(json.scores).forEach(function(key) {
      scores.push([json.scores[key], '<tr><td>' + key + '</td><td>' + json.scores[key] + '</td></tr>']);
    });
    scores = scores.sort(function(a, b) {return b[0] - a[0]});
    var table = ''
    scores.forEach(function(element) {
      table += element[1];
    })
    document.getElementById('scores').innerHTML = table;
  }
}

var btn = ['A', 'B', 'C', 'D']
btn.forEach(function(button) {
  document.getElementById(button).addEventListener("click", function() {
    if (lastSendId !== questionId) {
      var answer = button.charCodeAt(0) - 65;
      var answerJson = { username: username, questionId: questionId, answer: answer};
      console.log("going to send answer:");
      console.log(answerJson);
      connection.send(JSON.stringify(answerJson));
      lastSendId = questionId;
      document.getElementById(button).blur();
      if (answer == correctAnswer) {
        document.getElementById(button).className = "btn btn-success";
      } else {
        document.getElementById(button).className = "btn btn-danger";
        document.getElementById(btn[correctAnswer]).className = "btn btn-success";
      }
    }
  })
});

var countdownDiv = document.getElementById('countdown');

var countdown = function() {
  if (timeToAnswer > 0) {
    timeToAnswer--;
    countdownDiv.innerHTML = 'You still have ' + (parseInt(timeToAnswer / 10)) + '.' + (timeToAnswer % 10) +
      ' second to answer';
  }
}

setInterval(countdown, 100);

document.getElementById("exit").addEventListener("click", function() {
  connection.send(JSON.stringify({"exit": true}));
});