import threading
import time

EXPECTED_VOTES = 3


class voteStateThread(threading.Thread):
    def __init__(self, vote_map, logger):
        super(voteStateThread, self).__init__()
        self.vote_map = vote_map
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
                del self.vote_map[curr_timestamp]

    def join(self, timeout=None):
        self.alive = False
