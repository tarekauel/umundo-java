# TK Quizduell - Features
- quizduell like game using uMundo for communication
- users can join at any point in time
- new users can answer the next question
- one node is elected as leader:
  - sends questions
  - evaluates answers
- if the leader becomes unresponsive, all nodes start a leader election:
  - each node has a unqiue long typed priority
  - lower priority value means higher priority
  - if a node misses the heartbeat from the leader for 5 seconds, it starts the election
    - each node sends his own priority until it receives a message with a higher priority
    - if there is no message with a higher priority for a certain time, the node becomes the master
    - the elected node starts sending heartbeats
- two language bindings: Java and Python
  - Java runs on any OS
  - Python uses Linux bindings
  
#### Usage description can be found in the readmes in the subfolders of the clients
