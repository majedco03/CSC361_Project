"""
actully i tried 3 times to implement a RL but it still not working as i tried some
algorithmes and approaches I found on the internet like 
Q-learning and epsilon-greedy but the results were not good enough

so i decided to do this experiment to see if it will work or not 
becouse I need another agent so i can make it play against the miniMax agent
and collect data from the games to train a third agent using supervised learning


my idea here will be to implement another miniMax agent but it will
re-evaluate the heutistic after each full game
and adjust the weights of the heuristics based on the game outcome
this will make the agent adapte to the opponent strategy over time
"""

import math
import os
from board import Board
import json

# Get the directory where this script is located
scriptDir = os.path.dirname(os.path.abspath(__file__))
weightsFile = os.path.join(scriptDir, 'agent_weights.json')

class EvolvingMinimaxAgent:

    def __init__(self, player):
        self.player = player
        # Extended weights for comprehensive heuristic evaluation
        # More features = more learning opportunities
        self.weights = {
            # Offensive patterns
            'three': 100, # 3 in a row with 1 empty
            'two': 15, # 2 in a row with 2 empty
            'twoOpen': 25, # 2 in a row with empty on BOTH sides
            'onePotential': 3, # 1 piece with 3 empty (building potential)
            
            # Defensive patterns (negative values)
            'oppThree': -120, # Block opponent's 3
            'oppTwo': -20, # Block opponent's 2
            'oppTwoOpen': -35, # Open 2s are more dangerous
            
            # Positional weights
            'center': 5, # Center column control
            'centerAdjacent': 3, # Columns adjacent to center
            'bottomRow': 4, # Control of bottom row
            'heightPenalty': -2, # Penalty for pieces too high (less stable)
            
            # Structural patterns
            'doubleThreat': 80, # Two ways to win
            'blockedThree': -10,  # Our 3 that's blocked on both sides
            'trapSetup': 40, # Setting up unavoidable wins
            
            # Tempo and mobility
            'mobility': 2, # Number of valid moves available
            'threatCount': 15, # Total number of threats we have
            'oppThreatCount': -20, # Total threats opponent has
            
            # Edge control
            'edgePenalty': -1, # Slight penalty for edge columns
        }
        self.lastGameBoards = []
        self.lastGameResult = 0
        self.depth = 6
        self.loadWeights()

    def evaluateWindow(self, window, player):
        # same approach as regular minimax but with a high more detailed scoring
        score = 0
        opponent = 3 - player
        playerCount = window.count(player)
        oppCount = window.count(opponent)
        emptyCount = window.count(0)
        
        # Only evaluate if window is not mixed (contains only one player's pieces + empty)
        if playerCount > 0 and oppCount > 0:
            return 0  # Blocked window, no value
        
        # Offensive patterns
        if playerCount == 4:
            score += 10000  # Winning!
        elif playerCount == 3 and emptyCount == 1:
            score += self.weights['three']
        elif playerCount == 2 and emptyCount == 2:
            score += self.weights['two']
        elif playerCount == 1 and emptyCount == 3:
            score += self.weights['onePotential']
        
        # Defensive patterns
        if oppCount == 4:
            score -= 10000  # Opponent wins
        elif oppCount == 3 and emptyCount == 1:
            score += self.weights['oppThree']  # Already negative
        elif oppCount == 2 and emptyCount == 2:
            score += self.weights['oppTwo']
        
        return score

    def heuristicEvaluation(self, board, player):
        # deeper and more complecated evaluation
        score = 0
        opponent = 3 - player
        
        # positional evaluations
        
        # Center column control (most important column)
        centerCol = board.cols // 2
        for r in range(board.rows):
            if board.board[r][centerCol] == player:
                score += self.weights['center']
            elif board.board[r][centerCol] == opponent:
                score -= self.weights['center']
        
        # Adjacent to center columns
        for adjCol in [centerCol - 1, centerCol + 1]:
            if 0 <= adjCol < board.cols:
                for r in range(board.rows):
                    if board.board[r][adjCol] == player:
                        score += self.weights['centerAdjacent']
                    elif board.board[r][adjCol] == opponent:
                        score -= self.weights['centerAdjacent']
        
        # Bottom row control (foundation)
        bottomRow = board.rows - 1
        for c in range(board.cols):
            if board.board[bottomRow][c] == player:
                score += self.weights['bottomRow']
            elif board.board[bottomRow][c] == opponent:
                score -= self.weights['bottomRow']
        
        # Height penalty (pieces high up are less stable)
        for r in range(board.rows):
            heightFactor = (board.rows - 1 - r) / board.rows  # 0 at bottom, ~1 at top
            for c in range(board.cols):
                if board.board[r][c] == player:
                    score += self.weights['heightPenalty'] * heightFactor
                elif board.board[r][c] == opponent:
                    score -= self.weights['heightPenalty'] * heightFactor
        
        # Edge column penalty
        for r in range(board.rows):
            if board.board[r][0] == player or board.board[r][board.cols-1] == player:
                score += self.weights['edgePenalty']
            if board.board[r][0] == opponent or board.board[r][board.cols-1] == opponent:
                score -= self.weights['edgePenalty']
        
        # pattern evaluations with strategic bonuses
        
        myThreats = 0
        oppThreats = 0
        myOpenTwos = 0
        oppOpenTwos = 0
        
        # Horizontal patterns
        for r in range(board.rows):
            rowArray = [board.board[r][c] for c in range(board.cols)]
            for c in range(board.cols - 3):
                window = rowArray[c:c + 4]
                score += self.evaluateWindow(window, player)
                
                # Count threats
                if window.count(player) == 3 and window.count(0) == 1:
                    myThreats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    oppThreats += 1
                
                # Detect open twos (empty on both ends)
                if window.count(player) == 2 and window.count(0) == 2:
                    if c > 0 and c + 4 < board.cols:
                        if rowArray[c-1] == 0 and rowArray[c+4] == 0:
                            myOpenTwos += 1
                if window.count(opponent) == 2 and window.count(0) == 2:
                    if c > 0 and c + 4 < board.cols:
                        if rowArray[c-1] == 0 and rowArray[c+4] == 0:
                            oppOpenTwos += 1
        
        # Vertical patterns
        for c in range(board.cols):
            colArray = [board.board[r][c] for r in range(board.rows)]
            for r in range(board.rows - 3):
                window = colArray[r:r + 4]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    myThreats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    oppThreats += 1
        
        # Positive diagonal (bottom-left to top-right)
        for r in range(board.rows - 3):
            for c in range(board.cols - 3):
                window = [board.board[r + i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    myThreats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    oppThreats += 1
        
        # Negative diagonal (top-left to bottom-right)
        for r in range(3, board.rows):
            for c in range(board.cols - 3):
                window = [board.board[r - i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    myThreats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    oppThreats += 1
        
        # strategic bonuses based on pattern counts
        
        # Threat counting bonus
        score += myThreats * self.weights['threatCount']
        score += oppThreats * self.weights['oppThreatCount']
        
        # Open twos bonus (more dangerous than regular twos)
        score += myOpenTwos * self.weights['twoOpen']
        score += oppOpenTwos * self.weights['oppTwoOpen']
        
        # Double threat detection (having 2+ threats = likely win)
        if myThreats >= 2:
            score += self.weights['doubleThreat']
        if oppThreats >= 2:
            score -= self.weights['doubleThreat'] * 1.2  # Slightly more urgent to block
        
        # Mobility (having options is good)
        validMoves = len(board.getValidMoves())
        score += validMoves * self.weights['mobility']
        
        return score
    
    def result(self, board, action):
        newBoard = board.copy()
        newBoard.dropPiece(action)
        return newBoard
    

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
    
    def record_game_state(self, board):
        # Store a copy of the board state
        self.lastGameBoards.append(board.copy())

    
    def finalize_game(self, board):
        # Determine game result
        if board.checkWinState() == self.player:
            self.lastGameResult = 1  # win
        elif board.checkWinState() == 3 - self.player:
            self.lastGameResult = -1 # loss
        else:
            self.lastGameResult = 0  # draw or ongoing
        self.adjustWeights()
        self.saveWeights()
        self.lastGameBoards = []  # Clear for next game

    def adjustWeights(self):
        # Analyze game statistics will give more detailed insights and help to much more effective
        # learning from the game
        if not self.lastGameBoards or len(self.lastGameBoards) < 2:
            return
        
        lr = 0.03  # Learning rate
        opponent = 3 - self.player
        
        stats = {
            'myThrees': 0, 'oppThrees': 0,
            'myTwos': 0, 'oppTwos': 0,
            'myOpenTwos': 0, 'oppOpenTwos': 0,
            'centerControl': 0, 'adjacentControl': 0,
            'bottomControl': 0, 'edgePieces': 0,
            'myDoubleThreats': 0, 'oppDoubleThreats': 0,
            'avgMobility': 0, 'highPieces': 0,
        }
        
        # Analyze critical positions (last portion of game)
        criticalBoards = self.lastGameBoards[-min(10, len(self.lastGameBoards)):]
        centerCol = 3 
        
        for board in criticalBoards:
            threatsThisBoard = 0
            oppThreatsThisBoard = 0
            
            # Horizontal analysis
            for r in range(board.rows):
                rowArray = [board.board[r][c] for c in range(board.cols)]
                for c in range(board.cols - 3):
                    window = rowArray[c:c + 4]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        stats['myThrees'] += 1
                        threatsThisBoard += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        stats['oppThrees'] += 1
                        oppThreatsThisBoard += 1
                    if window.count(self.player) == 2 and window.count(0) == 2:
                        stats['myTwos'] += 1
                        # Check if open on both sides
                        if c > 0 and c + 4 < board.cols and rowArray[c-1] == 0 and rowArray[c+4] == 0:
                            stats['myOpenTwos'] += 1
                    if window.count(opponent) == 2 and window.count(0) == 2:
                        stats['oppTwos'] += 1
                        if c > 0 and c + 4 < board.cols and rowArray[c-1] == 0 and rowArray[c+4] == 0:
                            stats['oppOpenTwos'] += 1
            
            # Vertical analysis
            for c in range(board.cols):
                for r in range(board.rows - 3):
                    window = [board.board[r + i][c] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        stats['myThrees'] += 1
                        threatsThisBoard += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        stats['oppThrees'] += 1
                        oppThreatsThisBoard += 1
            
            # Diagonal analysis
            for r in range(board.rows - 3):
                for c in range(board.cols - 3):
                    window = [board.board[r + i][c + i] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        threatsThisBoard += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        oppThreatsThisBoard += 1
            
            for r in range(3, board.rows):
                for c in range(board.cols - 3):
                    window = [board.board[r - i][c + i] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        threatsThisBoard += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        oppThreatsThisBoard += 1
            
            # Double threat detection
            if threatsThisBoard >= 2:
                stats['myDoubleThreats'] += 1
            if oppThreatsThisBoard >= 2:
                stats['oppDoubleThreats'] += 1
            
            # Positional analysis
            for r in range(board.rows):
                for c in range(board.cols):
                    if board.board[r][c] == self.player:
                        if c == centerCol:
                            stats['centerControl'] += 1
                        elif c in [centerCol - 1, centerCol + 1]:
                            stats['adjacentControl'] += 1
                        if r == board.rows - 1:
                            stats['bottomControl'] += 1
                        if c == 0 or c == board.cols - 1:
                            stats['edgePieces'] += 1
                        if r < 2:  # Top two rows
                            stats['highPieces'] += 1
                    elif board.board[r][c] == opponent:
                        if c == centerCol:
                            stats['centerControl'] -= 1
                        elif c in [centerCol - 1, centerCol + 1]:
                            stats['adjacentControl'] -= 1
            
            stats['avgMobility'] += len(board.getValidMoves())
        
        stats['avgMobility'] /= len(criticalBoards)
        
        # adjust weights based on game result and stats
        
        if self.lastGameResult == 1:  # WIN
            # boost good moves
            if stats['myThrees'] > stats['oppThrees']:
                self.weights['three'] *= (1 + lr)
            if stats['myTwos'] > stats['oppTwos']:
                self.weights['two'] *= (1 + lr * 0.7)
            if stats['myOpenTwos'] > 0:
                self.weights['twoOpen'] *= (1 + lr)
            if stats['myDoubleThreats'] > 0:
                self.weights['doubleThreat'] *= (1 + lr)
                self.weights['trapSetup'] *= (1 + lr * 0.5)
            if stats['centerControl'] > 0:
                self.weights['center'] *= (1 + lr * 0.5)
                self.weights['centerAdjacent'] *= (1 + lr * 0.3)
            if stats['bottomControl'] > 0:
                self.weights['bottomRow'] *= (1 + lr * 0.3)
            
            # do not over-defend when wining
            self.weights['oppThree'] *= (1 - lr * 0.2)
            self.weights['oppTwo'] *= (1 - lr * 0.2)
            
        elif self.lastGameResult == -1:  # LOSS
            # boost defense
            self.weights['oppThree'] *= (1 + lr * 1.2)
            self.weights['oppTwo'] *= (1 + lr * 0.8)
            if stats['oppOpenTwos'] > stats['myOpenTwos']:
                self.weights['oppTwoOpen'] *= (1 + lr)
            if stats['oppDoubleThreats'] > stats['myDoubleThreats']:
                self.weights['doubleThreat'] *= (1 + lr * 0.5)
            
            # also boost offense - passive play loses
            if stats['myThrees'] < stats['oppThrees']:
                self.weights['three'] *= (1 + lr * 0.5)
            if stats['centerControl'] < 0:
                self.weights['center'] *= (1 + lr * 0.7)
                self.weights['centerAdjacent'] *= (1 + lr * 0.5)
            
            # adjust positional play
            if stats['edgePieces'] > 3:
                self.weights['edgePenalty'] *= (1 + lr * 0.5)  # More penalty
            if stats['highPieces'] > 3:
                self.weights['heightPenalty'] *= (1 + lr * 0.3)
            
            # maintain more choices
            self.weights['mobility'] *= (1 + lr * 0.3)
            
        else:  # draw
            # Small adjustments toward more aggressive play
            self.weights['three'] *= (1 + lr * 0.2)
            self.weights['threatCount'] *= (1 + lr * 0.1)
        
        # pull weights gently toward defaults
        defaults = {
            'three': 100, 'two': 15, 'twoOpen': 25, 'onePotential': 3,
            'oppThree': -120, 'oppTwo': -20, 'oppTwoOpen': -35,
            'center': 5, 'centerAdjacent': 3, 'bottomRow': 4,
            'heightPenalty': -2, 'doubleThreat': 80, 'blockedThree': -10,
            'trapSetup': 40, 'mobility': 2, 'threatCount': 15,
            'oppThreatCount': -20, 'edgePenalty': -1
        }
        decay = 0.02  # gently pull toward defaults
        for key in self.weights:
            if key in defaults:
                self.weights[key] = self.weights[key] * (1 - decay) + defaults[key] * decay
        
        resultStr = "WIN" if self.lastGameResult == 1 else "LOSS" if self.lastGameResult == -1 else "DRAW"
        print(f"{resultStr} | my_3s:{stats['myThrees']} opp_3s:{stats['oppThrees']} center:{stats['centerControl']:+d} dbl_threats:{stats['myDoubleThreats']}/{stats['oppDoubleThreats']}")
        print(f"  → three={self.weights['three']:.0f}, opp_three={self.weights['oppThree']:.0f}, dbl_threat={self.weights['doubleThreat']:.0f}")


    def saveWeights(self):
        with open(weightsFile, 'w') as f:
            json.dump(self.weights, f, indent=2)

    def loadWeights(self):
        # Store defaults to merge with loaded weights
        defaultWeights = self.weights.copy()
        try:
            with open(weightsFile, 'r') as f:
                loaded = json.load(f)
                # Merge: use loaded values where available, keep defaults for new keys
                for key in defaultWeights:
                    if key in loaded:
                        self.weights[key] = loaded[key]
                print(f"Loaded weights: {len(loaded)} keys found, {len(defaultWeights)} total keys")
        except FileNotFoundError:
            print("No saved weights found, using defaults")  
