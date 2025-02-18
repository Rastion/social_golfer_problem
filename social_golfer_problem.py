import random
from qubots.base_problem import BaseProblem
import os

class SocialGolferProblem(BaseProblem):
    """
    Social Golfer Problem

    In a social golfer setting, a club organizes play over several weeks.
    Each week the golfers are divided into groups of equal size. The goal is
    to schedule the groups over the weeks such that any pair of golfers meets
    at most once (or, equivalently, to minimize redundant meetings beyond the first).

    Instance File Format:
      - Three integers on a single line:
          nb_groups  group_size  nb_weeks
      - The total number of golfers is nb_groups * group_size.

    Decision Variables:
      A candidate solution is represented as a list of length nb_weeks.
      Each element (week) is a list of nb_groups groups (each a list of golfer indices).
      In a valid solution, each week every golfer (from 0 to nb_golfers-1) appears exactly once.

    Objective:
      Minimize the total number of redundant meetings. For each unordered pair of golfers,
      if they are scheduled to meet in the same group more than once, each meeting beyond
      the first is counted as a redundancy.
    """

    def __init__(self, instance_file):
        self.instance_file = instance_file
        self._load_instance(instance_file)

    def _load_instance(self, filename):

         # Resolve relative path with respect to this module’s directory.
        if not os.path.isabs(filename):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, filename)

        # Read three integers from the file: nb_groups, group_size, nb_weeks.
        with open(filename, "r") as f:
            tokens = f.read().split()
        if len(tokens) < 3:
            raise ValueError("Instance file must contain at least 3 integers.")
        self.nb_groups = int(tokens[0])
        self.group_size = int(tokens[1])
        self.nb_weeks = int(tokens[2])
        self.nb_golfers = self.nb_groups * self.group_size

    def evaluate_solution(self, candidate) -> float:
        """
        Evaluate the candidate solution.

        Candidate format:
            A list of length nb_weeks.
            Each element is a list of nb_groups groups (lists of golfer indices).
            For example, candidate[w][gr] is the list of golfers in group gr during week w.

        The function computes the total number of redundant meetings. For each pair of golfers,
        if they meet more than once over the weeks, the redundancy is (meetings - 1).

        If any week does not form a valid partition of all golfers (i.e. some golfers are missing
        or repeated, or a group does not have exactly group_size members), a heavy penalty is added.
        """
        penalty = 0
        # Validate each week's grouping.
        all_golfers = set(range(self.nb_golfers))
        for w, week in enumerate(candidate):
            # Check that there are exactly nb_groups groups
            if len(week) != self.nb_groups:
                penalty += 1e6
                continue
            # Flatten the groups.
            week_golfers = [gf for group in week for gf in group]
            if len(week_golfers) != self.nb_golfers:
                penalty += 1e6
            if set(week_golfers) != all_golfers:
                penalty += 1e6
            # Check each group has exactly group_size members.
            for group in week:
                if len(group) != self.group_size:
                    penalty += 1e6

        # Compute meeting counts for each unordered pair of golfers.
        # Initialize a 2D matrix (only use indices where gf0 < gf1).
        meeting_count = [[0 for _ in range(self.nb_golfers)] for _ in range(self.nb_golfers)]
        for week in candidate:
            for group in week:
                # For each pair in the group.
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        gf0 = group[i]
                        gf1 = group[j]
                        # Assume golfers are numbered 0...nb_golfers-1.
                        meeting_count[gf0][gf1] += 1

        redundant = 0
        for gf0 in range(self.nb_golfers):
            for gf1 in range(gf0 + 1, self.nb_golfers):
                # Each pair meeting more than once is penalized.
                if meeting_count[gf0][gf1] > 1:
                    redundant += meeting_count[gf0][gf1] - 1

        return redundant + penalty

    def random_solution(self):
        """
        Generate a random candidate solution.

        For each week, generate a random permutation of all golfers and partition
        the list into nb_groups groups of size group_size.
        """
        candidate = []
        golfers = list(range(self.nb_golfers))
        for _ in range(self.nb_weeks):
            random.shuffle(golfers)
            week = []
            for gr in range(self.nb_groups):
                start = gr * self.group_size
                end = start + self.group_size
                group = golfers[start:end]
                week.append(group)
            candidate.append(week)
        return candidate
