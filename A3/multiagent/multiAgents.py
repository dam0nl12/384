# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

# TA says i'm allowed to include this library.
import sys

from game import Agent


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        # I forgot to delete the line below in Part I.
        # newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"

        # A capable reflex agent must consider both food locations and ghost locations to perform well.
        food_score = 0
        ghost_score = 0
        initial_score = successorGameState.getScore()

        # I tried different ints for RECIPROCAL_DIVISOR, 10 and 11 are the best:
        # Any number >= 12 will cause the slow performance, since the pacman will play too safely, slow. food_score will
        # be small, and the pacman thinks that staying is the best move. Any number <= 9 will let the pacman like taking
        # high risks. food_score will be big, the pacman always wants to move.
        RECIPROCAL_DIVISOR = 10

        # Firstly, evaluate the scores for the foods' locations.
        # Get every distance to every food. If this is a empty list, then the the pacman will have eaten all foods.
        foods_dis = [manhattanDistance(food_pos, newPos) for food_pos in newFood.asList()]

        # Case 1: There is still some food(s) left, then find the distance to the closest food.
        if len(foods_dis) > 0:
            closest_food_dis = min(foods_dis)
            food_score = RECIPROCAL_DIVISOR / closest_food_dis

        # Case 2: the pacman will eat the last food, if it goes to this position. This food is the final target.
        else:
            food_score = sys.maxint

        # Secondly, evaluate the scores for ghosts' locations.
        # Get every distance to every ghost. There should be at least one ghost.
        ghosts_dis = [manhattanDistance(ghost_state.getPosition(), newPos) for ghost_state in newGhostStates]

        # Case 1: There is some ghost(s) close to the pacman.
        # Less than 2 steps away from a ghost isn't safe. The pacman won't have enough time to eat a node and escape.
        if any([True if dis <= 1 else False for dis in ghosts_dis]):
            ghost_score = sys.maxint

        # Case 2: All ghosts are at least 2 steps away. The pacman is relatively safe now.
        else:
            # sum(ghosts_dis) performs better than min(ghosts_dis), probably because sum represents a general trend.
            ghost_score = RECIPROCAL_DIVISOR / sum(ghosts_dis)

        return initial_score + food_score - ghost_score


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"

        # Get all successor-states of gameState.
        legal_actions = gameState.getLegalActions()
        successor_game_states = [gameState.generateSuccessor(0, action) for action in legal_actions]

        # Find the successor state with the max DFMinMax score.
        # Now, player is not 0, but 1, because we are at one level below the gameState.
        successors_scores = [self.DFMinMax(successor_state, 1, 0) for successor_state in successor_game_states]
        best_action_index = successors_scores.index(max(successors_scores))

        # len(legal_actions) == len(successor_game_states) == len(successors_scores).
        return legal_actions[best_action_index]

    # DFMinMax = Depth-First Implementation of MiniMax in the lecture note (p38).
    def DFMinMax(self, state, player, depth):
        # Base case 1: No more legal actions left for current player: player just won/lost.
        if state.isWin() or state.isLose():

            return self.evaluationFunction(state)

        # Base case 2: Depth reaches the max depth.
        if player == state.getNumAgents():
            if depth == self.depth - 1:

                # These 2 base cases need to be separated to avoid the error:
                # trying to get_score() form a non-terminated node.
                return self.evaluationFunction(state)

            # If search is not ended above,
            # then player needs to be changed back to 0 (the pacman) once it reaches the certain levels.
            player = 0

        # Apply player's action to get successor states.
        legal_actions = state.getLegalActions(player)
        successors_game_states = [state.generateSuccessor(player, action) for action in legal_actions]

        # If player is a ghost, i.e. player = MIN.
        if player != 0:

            return min([self.DFMinMax(successor_state, player + 1, depth) for successor_state in
                        successors_game_states])

        # Else, player is the pacman, i.e. player = MAX.
        else:

            return max([self.DFMinMax(successor_state, player + 1, depth + 1) for successor_state in
                        successors_game_states])


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        # The lecture note (p48).

        legal_actions = gameState.getLegalActions(0)
        alpha = -sys.maxint
        beta = sys.maxint
        final_action = None

        # Initial call. Pruning starts from the top node.
        for action in legal_actions:

            # AlphaBeta(START_NODE, Player, -infinity, +infinity)
            new_alpha = max(alpha, self.ABPruning(gameState.generateSuccessor(0, action), 1, 0, alpha, beta))

            # Only care about alpha, since player 0, i.e. pacman, is a MAX player.
            # Find a larger alpha, and better action.
            if new_alpha > alpha:
                alpha = new_alpha
                final_action = action

            if beta <= alpha:
                break

        return final_action

    # ABPruning = Alpha-Bete Pruning in the lecture note (p47).
    def ABPruning(self, state, player, depth, alpha, beta):
        # Really similar base cases to DFMinMax().
        if state.isWin() or state.isLose():

            return self.evaluationFunction(state)

        if player == state.getNumAgents():
            if depth == self.depth - 1:

                return self.evaluationFunction(state)

            player = 0

        legal_actions = state.getLegalActions(player)
        # Don't compute all successor states here! We want to prune some successor states, not expand all of them.

        # Update alpha and beta.
        # If player is the pacman, i.e. player = MAX.
        if player == 0:

            for action in legal_actions:

                alpha = max(alpha, self.ABPruning(state.generateSuccessor(player, action), player + 1, depth + 1, alpha, beta))
                if beta <= alpha:
                    break

            return alpha

        # Else, if player is a ghost, i.e. player = MIN.
        else:

            for action in legal_actions:

                beta = min(beta, self.ABPruning(state.generateSuccessor(player, action), player + 1, depth, alpha, beta))
                if beta <= alpha:
                    break

            return beta


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"

        # The codes below in this function are exactly the same as the codes of MinimaxAgent.getAction(gameState).

        legal_actions = gameState.getLegalActions()
        successor_game_states = [gameState.generateSuccessor(0, action) for action in legal_actions]

        successors_scores = [self.Expectimax(successor_state, 1, 0) for successor_state in successor_game_states]
        best_action_index = successors_scores.index(max(successors_scores))

        return legal_actions[best_action_index]

    def Expectimax(self, state, player, depth):
        if state.isWin() or state.isLose():

            return self.evaluationFunction(state)

        if player == state.getNumAgents():
            if depth == self.depth - 1:

                return self.evaluationFunction(state)

            player = 0

        legal_actions = state.getLegalActions(player)
        successors_game_states = [state.generateSuccessor(player, action) for action in legal_actions]

        # The only difference in implementation of Expectimax search and Minimax search, is that at a min node,
        # Expectimax search will return the average value over its children as opposed to the minimum value.
        # If player is a ghost, i.e. player = MIN.
        if player != 0:
            min_scores = [self.Expectimax(successor_state, player + 1, depth) for successor_state
                          in successors_game_states]

            # Return float, not int.
            return float(sum(min_scores)) / float(len(min_scores))

        # Else, player is the pacman, i.e. player = MAX.
        else:

            return max([self.Expectimax(successor_state, player + 1, depth + 1) for successor_state in
                        successors_game_states])


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"

    # Most codes are copied from ReflexAgent.EvaluationFunction(currentGameState, action).

    # Info of the current state.
    pacman_pos = currentGameState.getPacmanPosition()
    foods = currentGameState.getFood()
    ghost_states = currentGameState.getGhostStates()

    food_score = 0
    ghost_score = 0
    initial_score = currentGameState.getScore()
    RECIPROCAL_DIVISOR = 10

    # Firstly, evaluate the scores for the foods' locations.
    foods_dis = [manhattanDistance(food_pos, pacman_pos) for food_pos in foods.asList()]

    # Case 1: There is still some food(s) left, then find the distance to the closest food.
    # Avoid divided-by-zero error.
    if len(foods_dis) > 0:
        closest_food_dis = min(foods_dis)
        food_score = RECIPROCAL_DIVISOR / closest_food_dis

    # We don't need consider the Case of (len(foods_dis) == 0) any more, because we are evaluating a state, not an
    # action. We don't need force the pacman to choose the optimal action. Also, if len(foods_dis) == 0, then the game
    # will be over.

    # Secondly, evaluate the scores for the ghosts' locations.
    ghosts_dis = [manhattanDistance(ghost_state.getPosition(), pacman_pos) for ghost_state in ghost_states]
    # The ghost-hunting feature should be included; otherwise, the final scores will usually be less than 1000.
    scared_times = [ghost_state.scaredTimer for ghost_state in ghost_states]

    # Thanks Professor Allin for the hints:
    # 1) The score for hunting-ghost should not be too high, such as sys.maxint. The scale should be modified.
    # 2) Use a for-loop rather than trying to finish everything by list-comprehension.
    for i in range(len(ghosts_dis)):

        ghost_dis = ghosts_dis[i]
        # Avoid divided-by-zero error.
        if ghost_dis > 0:
            # Case 1: The ghost is scared and the pacman can reach it before the scared time runs out, then the pacman
            # should try to hunt it for the higher points rather than eating foods.
            scared_time = scared_times[i]
            if scared_time > 0 and scared_time > ghost_dis:
                # We want the final score to be high, so we should decrease the ghost_score here.
                # 18 works better than any number between 10 and 20.
                ghost_score -= 18 * RECIPROCAL_DIVISOR / ghosts_dis[i]

            # Case 2: The ghost is not scared, then the pacman should stay away from it.
            else:
                # Similar to the sum() in ReflexAgent.EvaluationFunction(currentGameState, action).
                ghost_score += RECIPROCAL_DIVISOR / ghosts_dis[i]

    return initial_score + food_score - ghost_score


# Abbreviation
better = betterEvaluationFunction
