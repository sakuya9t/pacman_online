# Synchronization of Game Screens

In our multiplayer pacman game, it is important that every players' game screen are synchronized. If game screens are not synchronized, every players' game will be in different game state. Due to network latency, there will always be some delay to send message to other player when the local process can receive the message and update game state immediately.  For example, in the figure below, the first game screen will be the game screen of the player that controls the blue pacman and the second game screen will be the one for the player of red pacman. The blue pacman in the first game state can happily enter the red territory and head up to avoid the red ghost. However, in the second game state, the blue pacman cannot enter the red territory because the red ghost is blocking the entrance. The inconsistent game state between   players will make our multiplayer game meaningless.

![unsync1](image\unsync1.png)

![unsync2](image\unsync2.png)

In order to solve the synchronization problem, we modified the total ordering (TO) multicast algorithm to order the control messages for each agent. The idea is to update the state of the agents in the same frequency. No one can move another step until every other agent has taken an action. 

## Assumptions

* Processes and connections will not fail.
* Messages sent by the same process arrive in sequence.

## Algorithms

The approach we used to implement total ordering multicast is to have a sequencer to maintain the messages and ordering that should be delivered across all the processes. On initialization, every processes will maintain a process sequence number *p_seq*, 4 action queues and 4 hold-back queues. When a process want to send a control message of its agent, it B-multicast <*message_type, unique_message_id, message*> to all the processes including the sequencer. When a process receives the value, it will place the <*unique_message_id, message*> in the hold-back queue corresponds to the agent. The sequencer process will actively check the hold-back queues to see if all the agents have decided their move. If so, it will choose the latest decisions for all the agents and B-multicast one control message <*message_type, unique_message_id, group _sequence_number (g_seq)*>  for each agent to all the processes. When a process receives a message from the sequencer, it will update its game state correspondingly.

The pseudocode is shown below:

```
1. For each process p
On initialization: p_seq = 0, action_q = Queue(), hold_q = Queue()

To TO-multicast message:
	B-multicast(<HOLD-BACK, msg_id, msg>)
	
On B-deliver(<HOLD-BACK, msg_id, msg>):
	hold_q.push(<msg_id, msg>)

On B-deliver(<DELIVER, msg_id, g_seq>):
	if p_seq == g_seq:
		find <msg_id, msg> in hold_q and delete the messages that arrives before msg_id
		action_q.push(msg_id)
		p_seq += 1
	else:
		hold and wait (didn't implement...)

2. For sequencer q:
On initialization: q_seq = 0

If all 4 hold_q have some value:
	Select the last message in all 4 hold_q
	for msg_id in selected_messges
        B-multicast(<DELIVER, msg_id, q_seq>)
        q_seq += 1
```

## Implementations



## Demo

## Reference

