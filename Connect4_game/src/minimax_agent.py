#MiniMax with Alpha-Beta Pruning Agent for a two-player game
#when its start to play it will watch the board and decide the best move
# it will have 3 levels of difficulty: easy, medium, hard
# easy : depth = 2
# medium : depth = 4
# hard : depth = 6
import math
import random
from board import Board

# problem formulation (based on the slides we saw in class):
"""
start state: current board state
player to move: self.board.turn
actions: valid columns to drop a piece
result (transition model): new board state after dropping a piece
terminal test: checkWin or checkDraw
utility function (for only terminal states): +100 for win, -100 for loss, 0 for draw
"""

"""
# after some search i found that a normal connect-4 game tree has a branching factor of about 7
# and around 4 trillion possible states
# so i will use depth limit approach with alpha-beta and heuristic evaluation function
#instead of apllying the minimax we learned in class
"""

"""
I have searched for heuristic evaluation functions for Connect-4
and found that its depends on 3 main factors:
1. 3 in a row and 1 empty space (considered as the most importan as the next move
will decide the game so : +100 for self, -120 for opponent since blocking is more important)
2. 2 in a row and 2 empty spaces : +10 for self, -15 for opponent
3. center column control : +3 for each piece in the center column
"""
class MinimaxAgent:

    def __init__(self, player, difficulty):
        self.player = player
        if difficulty == 'easy':
            self.depth = 2
        elif difficulty == 'medium':
            self.depth = 4
        elif difficulty == 'hard':
            self.depth = 6
        else:
            self.depth = 4  # default to medium

# heuristic evaluation function will devide the board into windows 
# of 4 and evaluate each window
    def evaluateWindow(self, window, player):
        score = 0
        opponent = 3 - player
        # Good scenarios
        if window.count(player) == 4:
            score += 1000 # winning move
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 100 # three in a row with one empty space
        elif window.count(player) == 2 and window.count(0) == 2:
            score += 10 # two in a row with two empty spaces
        
        # Bad scenarios
        if window.count(opponent) == 3 and window.count(0) == 1:
            score -= 120 # opponent three in a row with one empty space
        elif window.count(opponent) == 2 and window.count(0) == 2:
            score -= 15 # opponent two in a row with two empty spaces
        
        return score
    
    def heuristicEvaluation(self, board, player):
        score = 0
        
        # Center column control
        center_col = [board.board[r][board.cols // 2] for r in range(board.rows)]
        score += center_col.count(player) * 3
        
        # Horizontal
        for r in range(board.rows):
            row_array = [board.board[r][c] for c in range(board.cols)]
            for c in range(board.cols - 3):
                window = row_array[c:c + 4]
                score += self.evaluateWindow(window, player)
        
        # Vertical
        for c in range(board.cols):
            col_array = [board.board[r][c] for r in range(board.rows)]
            for r in range(board.rows - 3):
                window = col_array[r:r + 4]
                score += self.evaluateWindow(window, player)
        
        # Positive diagonal
        for r in range(board.rows - 3):
            for c in range(board.cols - 3):
                window = [board.board[r + i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
        
        # Negative diagonal
        for r in range(3, board.rows):
            for c in range(board.cols - 3):
                window = [board.board[r - i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
        
        return score 
    
    def result(self, board, action):
        new_board = board.copy() 
        new_board.dropPiece(action)
        return new_board
    

    def maxValue(self, board, depth, alpha, beta, player):
        # is it terminal state?
        if board.checkWinState() == player:
            return 1000
        elif board.checkWinState() == 3 - player:
            return -1000
        elif board.checkDrawState():
            return 0
        if depth == 0:
            return self.heuristicEvaluation(board, player)
        v = -math.inf
        for a in board.getValidMoves():
            v = max(v, self.minValue(self.result(board, a), depth - 1, alpha, beta, player))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def minValue(self, board, depth, alpha, beta, player):
        if board.checkWinState() == 3 - player:
            return -1000
        elif board.checkWinState() == player:
            return 1000
        elif board.checkDrawState():
            return 0
        if depth == 0:
            return self.heuristicEvaluation(board, player)
        v = math.inf
        for a in board.getValidMoves():
            v = min(v, self.maxValue(self.result(board, a), depth - 1, alpha, beta, player))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def alphaBetaSearch(self, board, depth):
        best_action = None
        best_value = -math.inf
        for action in board.getValidMoves():
            result_board = self.result(board, action)
            value = self.minValue(result_board, depth - 1, -math.inf, math.inf, self.player)
            if value > best_value:
                best_value = value
                best_action = action
        return best_action

    def get_move(self, game):
        return self.alphaBetaSearch(game, self.depth)
