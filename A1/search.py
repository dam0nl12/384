# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    from util import Stack

    s = Stack()
    # The first element is the current state(position),
    # the second element will be the path (list of directions) that eventually guides the pacman to the node.
    s.push([problem.getStartState(), []])

    # The path which the pacman has visited before. This is designed for the path-checking.
    # Using set instead of list, so we don't worry about adding any duplicated state into visited_path.
    visited_states = set()

    while not s.isEmpty():
        curr_state, path = s.pop()

        # Find the destination.
        if problem.isGoalState(curr_state):
            return path

        # Else, keep finding.
        elif curr_state not in visited_states:
            visited_states.add(curr_state)

            # new_cost doesn't have any use in this loop.
            for successor_state, action, new_cost in problem.getSuccessors(curr_state):

                if successor_state not in visited_states:
                    # Tried to use path.append(action) here, but it does not work.
                    s.push([successor_state, path + [action]])


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    from util import Queue

    # The implementation of BFS should be similar with the one of DFS, except that we are now using a Queue,
    # not a Stack.
    q = Queue()
    # The third element is cost from a parent state to one of its successor_states.
    start_state = problem.getStartState()
    q.push([start_state, [], 0])

    # Need for the cycle-checking.
    visited_states = {start_state: 0}

    # Cycle-checking is based on the algorithm.pdf.
    while not q.isEmpty():
        curr_state, path, cost = q.pop()

        # We want the optimal path.
        if cost <= visited_states[curr_state]:

            if problem.isGoalState(curr_state):
                return path

            for successor_state, action, new_cost in problem.getSuccessors(curr_state):

                if successor_state not in visited_states or cost + new_cost < visited_states[successor_state]:
                    q.push([successor_state, path + [action], cost + new_cost])
                    visited_states[successor_state] = cost + new_cost


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue

    # PriorityQueue should be used, due to the costs. UCS is similar with the BFS.
    pq = PriorityQueue()
    start_state = problem.getStartState()
    pq.push([start_state, [], 0], 0)

    visited_states = {start_state: 0}

    while not pq.isEmpty():
        curr_state, path, cost = pq.pop()

        if cost <= visited_states[curr_state]:

            if problem.isGoalState(curr_state):
                return path

            for successor_state, action, new_cost in problem.getSuccessors(curr_state):

                if successor_state not in visited_states or cost + new_cost < visited_states[successor_state]:
                    pq.push([successor_state, path + [action], cost + new_cost], cost + new_cost)
                    visited_states[successor_state] = cost + new_cost


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    from util import PriorityQueue

    # Similar with UCS, except that the priority is based on the evaluation function f:
    # f = g: cost of a move(0 at first) + h: Heuristic(0 at end)
    pq = PriorityQueue()
    start_state = problem.getStartState()
    pq.push([start_state, [], 0], 0)

    visited_states = {start_state: 0}

    while not pq.isEmpty():
        curr_state, path, cost = pq.pop()

        if cost <= visited_states[curr_state]:

            if problem.isGoalState(curr_state):
                return path

            for successor_state, action, g_cost in problem.getSuccessors(curr_state):

                if successor_state not in visited_states or \
                         cost + g_cost + heuristic(successor_state, problem) < visited_states[successor_state]:
                    # Don't add the heuristic cost to the third element in the list, since the third element is the
                    # cost between a parent_state and the successor_State.
                    pq.push([successor_state, path + [action], cost + g_cost],
                            cost + g_cost + heuristic(successor_state, problem))
                    visited_states[successor_state] = cost + g_cost + heuristic(successor_state, problem)


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
