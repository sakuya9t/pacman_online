import threading
import time


class voteStateThread(threading.Thread):
    def __init__(self, vote_map, decision_map, node_map, lock, logger):
        super(voteStateThread, self).__init__()
        self.vote_map = vote_map
        self.node_map = node_map
        self.decision_map = decision_map
        self.alive = True
        self.lock = lock
        self.logger = logger

    def run(self):
        while self.alive:
            if len(self.vote_map.keys()) == 0:
                time.sleep(0.1)
                continue

            expected_votes = self.node_map.size()
            self.lock.acquire()
            try:
                curr_timestamp = max(self.vote_map.iterkeys())
                votes = self.vote_map[curr_timestamp]
                # each decision requires 3 votes including p* and two other non-coordinator processes
                # If less than 3 connected (maybe old general dropped), only collect those connected.
                if len(votes) == expected_votes:
                    self.logger.info("Collected all votes for timestamp {timestamp}."
                                     .format(timestamp=curr_timestamp))
                    # make decision according to votes. If cannot make it, return nu.
                    decision = decide(votes)
                    self.decision_map[curr_timestamp] = decision
                    del self.vote_map[curr_timestamp]
            finally:
                self.lock.release()

    def join(self, timeout=None):
        self.alive = False


def decide(votes):
    if len(votes) == 0:
        return "null"
    elif len(votes) == 1:
        return votes[0]
    elif len(votes) == 2:
        if votes[0] == votes[1]:
            return votes[0]
        return "null"
    a, b, c = votes[0], votes[1], votes[2]
    if a == b:
        return a
    if a == c:
        return a
    if b == c:
        return b
    return "null"
