import threading
import time

EXPECTED_VOTES = 3


class voteStateThread(threading.Thread):
    def __init__(self, vote_map, decision_map, logger):
        super(voteStateThread, self).__init__()
        self.vote_map = vote_map
        self.decision_map = decision_map
        self.alive = True
        self.logger = logger

    def run(self):
        while self.alive:
            if len(self.vote_map.keys()) == 0:
                time.sleep(0.1)
                continue
            curr_timestamp = max(self.vote_map.iterkeys())
            votes = self.vote_map[curr_timestamp]
            # each decision requires 3 votes including p* and two other non-coordinator processes
            if len(votes) == EXPECTED_VOTES:
                self.logger.info("Collected all votes for timestamp {timestamp}."
                                 .format(timestamp=curr_timestamp))
                # make decision according to votes. If cannot make it, return nu.
                decision = decide(votes[0], votes[1], votes[2])
                self.decision_map[curr_timestamp] = decision
                del self.vote_map[curr_timestamp]

    def join(self, timeout=None):
        self.alive = False


def decide(a, b, c):
    if a == b:
        return a
    if a == c:
        return a
    if b == c:
        return b
    return "null"
