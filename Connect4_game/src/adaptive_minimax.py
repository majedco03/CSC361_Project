"""
actully i tried 3 times to implement a RL but it still not working as i tried some
algorithmes and approaches I found on the internet like 
Q-learning and epsilon-greedy but the results were not good enough

so i decided to do this experiment to see if it will work or not 
becouse I need another agent so i can make it play against the miniMax agent
and collect data from the games to train a third agent using supervised learning


my idea here will be to implement another miniMax agent but it will
re-evaluate the heutistic function after each full game
and adjust the weights of the heutistic function based on the game outcome
this will make the agent adapte to the opponent strategy over time
"""

import math
import os
from board import Board
import json

# Get the directory where this script is located
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_WEIGHTS_FILE = os.path.join(_SCRIPT_DIR, 'agent_weights.json')

class EvolvingMinimaxAgent:

    def __init__(self, player):
        self.player = player
        # Extended weights for comprehensive heuristic evaluation
        # More features = more learning opportunities
        self.weights = {
            # Offensive patterns
            'three': 100,              # 3 in a row with 1 empty
            'two': 15,                 # 2 in a row with 2 empty
            'two_open': 25,            # 2 in a row with empty on BOTH sides
            'one_potential': 3,        # 1 piece with 3 empty (building potential)
            
            # Defensive patterns (negative values)
            'opp_three': -120,         # Block opponent's 3
            'opp_two': -20,            # Block opponent's 2
            'opp_two_open': -35,       # Open 2s are more dangerous
            
            # Positional weights
            'center': 5,               # Center column control
            'center_adjacent': 3,      # Columns adjacent to center
            'bottom_row': 4,           # Control of bottom row
            'height_penalty': -2,      # Penalty for pieces too high (less stable)
            
            # Structural patterns
            'double_threat': 80,       # Two ways to win
            'blocked_three': -10,      # Our 3 that's blocked on both sides
            'trap_setup': 40,          # Setting up unavoidable wins
            
            # Tempo and mobility
            'mobility': 2,             # Number of valid moves available
            'threat_count': 15,        # Total number of threats we have
            'opp_threat_count': -20,   # Total threats opponent has
            
            # Edge control
            'edge_penalty': -1,        # Slight penalty for edge columns
        }
        self.last_game_boards = []
        self.last_game_result = 0
        self.depth = 6
        self.load_weights()

    def evaluateWindow(self, window, player):
        # same approach as regular minimax but with a high more detailed scoring
        score = 0
        opponent = 3 - player
        player_count = window.count(player)
        opp_count = window.count(opponent)
        empty_count = window.count(0)
        
        # Only evaluate if window is not mixed (contains only one player's pieces + empty)
        if player_count > 0 and opp_count > 0:
            return 0  # Blocked window, no value
        
        # Offensive patterns
        if player_count == 4:
            score += 10000  # Winning!
        elif player_count == 3 and empty_count == 1:
            score += self.weights['three']
        elif player_count == 2 and empty_count == 2:
            score += self.weights['two']
        elif player_count == 1 and empty_count == 3:
            score += self.weights['one_potential']
        
        # Defensive patterns
        if opp_count == 4:
            score -= 10000  # Opponent wins
        elif opp_count == 3 and empty_count == 1:
            score += self.weights['opp_three']  # Already negative
        elif opp_count == 2 and empty_count == 2:
            score += self.weights['opp_two']
        
        return score

    def heuristicEvaluation(self, board, player):
        # deeper and more complecated evaluation
        score = 0
        opponent = 3 - player
        
        # positional evaluations
        
        # Center column control (most important column)
        center_col = board.cols // 2
        for r in range(board.rows):
            if board.board[r][center_col] == player:
                score += self.weights['center']
            elif board.board[r][center_col] == opponent:
                score -= self.weights['center']
        
        # Adjacent to center columns
        for adj_col in [center_col - 1, center_col + 1]:
            if 0 <= adj_col < board.cols:
                for r in range(board.rows):
                    if board.board[r][adj_col] == player:
                        score += self.weights['center_adjacent']
                    elif board.board[r][adj_col] == opponent:
                        score -= self.weights['center_adjacent']
        
        # Bottom row control (foundation)
        bottom_row = board.rows - 1
        for c in range(board.cols):
            if board.board[bottom_row][c] == player:
                score += self.weights['bottom_row']
            elif board.board[bottom_row][c] == opponent:
                score -= self.weights['bottom_row']
        
        # Height penalty (pieces high up are less stable)
        for r in range(board.rows):
            height_factor = (board.rows - 1 - r) / board.rows  # 0 at bottom, ~1 at top
            for c in range(board.cols):
                if board.board[r][c] == player:
                    score += self.weights['height_penalty'] * height_factor
                elif board.board[r][c] == opponent:
                    score -= self.weights['height_penalty'] * height_factor
        
        # Edge column penalty
        for r in range(board.rows):
            if board.board[r][0] == player or board.board[r][board.cols-1] == player:
                score += self.weights['edge_penalty']
            if board.board[r][0] == opponent or board.board[r][board.cols-1] == opponent:
                score -= self.weights['edge_penalty']
        
        # pattern evaluations with strategic bonuses
        
        my_threats = 0
        opp_threats = 0
        my_open_twos = 0
        opp_open_twos = 0
        
        # Horizontal patterns
        for r in range(board.rows):
            row_array = [board.board[r][c] for c in range(board.cols)]
            for c in range(board.cols - 3):
                window = row_array[c:c + 4]
                score += self.evaluateWindow(window, player)
                
                # Count threats
                if window.count(player) == 3 and window.count(0) == 1:
                    my_threats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    opp_threats += 1
                
                # Detect open twos (empty on both ends)
                if window.count(player) == 2 and window.count(0) == 2:
                    if c > 0 and c + 4 < board.cols:
                        if row_array[c-1] == 0 and row_array[c+4] == 0:
                            my_open_twos += 1
                if window.count(opponent) == 2 and window.count(0) == 2:
                    if c > 0 and c + 4 < board.cols:
                        if row_array[c-1] == 0 and row_array[c+4] == 0:
                            opp_open_twos += 1
        
        # Vertical patterns
        for c in range(board.cols):
            col_array = [board.board[r][c] for r in range(board.rows)]
            for r in range(board.rows - 3):
                window = col_array[r:r + 4]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    my_threats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    opp_threats += 1
        
        # Positive diagonal (bottom-left to top-right)
        for r in range(board.rows - 3):
            for c in range(board.cols - 3):
                window = [board.board[r + i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    my_threats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    opp_threats += 1
        
        # Negative diagonal (top-left to bottom-right)
        for r in range(3, board.rows):
            for c in range(board.cols - 3):
                window = [board.board[r - i][c + i] for i in range(4)]
                score += self.evaluateWindow(window, player)
                
                if window.count(player) == 3 and window.count(0) == 1:
                    my_threats += 1
                if window.count(opponent) == 3 and window.count(0) == 1:
                    opp_threats += 1
        
        # strategic bonuses based on pattern counts
        
        # Threat counting bonus
        score += my_threats * self.weights['threat_count']
        score += opp_threats * self.weights['opp_threat_count']
        
        # Open twos bonus (more dangerous than regular twos)
        score += my_open_twos * self.weights['two_open']
        score += opp_open_twos * self.weights['opp_two_open']
        
        # Double threat detection (having 2+ threats = likely win)
        if my_threats >= 2:
            score += self.weights['double_threat']
        if opp_threats >= 2:
            score -= self.weights['double_threat'] * 1.2  # Slightly more urgent to block
        
        # Mobility (having options is good)
        valid_moves = len(board.getValidMoves())
        score += valid_moves * self.weights['mobility']
        
        return score
    
    def result(self, board, action):
        new_board = board.copy()
        new_board.drop_piece(action)
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
    
    def record_game_state(self, board):
        # Store a copy of the board state
        self.last_game_boards.append(board.copy())

    
    def finalize_game(self, board):
        # Determine game result
        if board.checkWinState() == self.player:
            self.last_game_result = 1  # win
        elif board.checkWinState() == 3 - self.player:
            self.last_game_result = -1 # loss
        else:
            self.last_game_result = 0  # draw or ongoing
        self.adjust_weights()
        self.save_weights()
        self.last_game_boards = []  # Clear for next game

    def adjust_weights(self):
        if not self.last_game_boards or len(self.last_game_boards) < 2:
            return
        
        lr = 0.03  # Learning rate
        opponent = 3 - self.player
        
        # Analyze game statistics will give more detailed insights and help to much more effective
        # learning from the game
        stats = {
            'my_threes': 0, 'opp_threes': 0,
            'my_twos': 0, 'opp_twos': 0,
            'my_open_twos': 0, 'opp_open_twos': 0,
            'center_control': 0, 'adjacent_control': 0,
            'bottom_control': 0, 'edge_pieces': 0,
            'my_double_threats': 0, 'opp_double_threats': 0,
            'avg_mobility': 0, 'high_pieces': 0,
        }
        
        # Analyze critical positions (last portion of game)
        critical_boards = self.last_game_boards[-min(10, len(self.last_game_boards)):]
        center_col = 3  # For 7-column board
        
        for board in critical_boards:
            threats_this_board = 0
            opp_threats_this_board = 0
            
            # Horizontal analysis
            for r in range(board.rows):
                row_array = [board.board[r][c] for c in range(board.cols)]
                for c in range(board.cols - 3):
                    window = row_array[c:c + 4]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        stats['my_threes'] += 1
                        threats_this_board += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        stats['opp_threes'] += 1
                        opp_threats_this_board += 1
                    if window.count(self.player) == 2 and window.count(0) == 2:
                        stats['my_twos'] += 1
                        # Check if open on both sides
                        if c > 0 and c + 4 < board.cols and row_array[c-1] == 0 and row_array[c+4] == 0:
                            stats['my_open_twos'] += 1
                    if window.count(opponent) == 2 and window.count(0) == 2:
                        stats['opp_twos'] += 1
                        if c > 0 and c + 4 < board.cols and row_array[c-1] == 0 and row_array[c+4] == 0:
                            stats['opp_open_twos'] += 1
            
            # Vertical analysis
            for c in range(board.cols):
                for r in range(board.rows - 3):
                    window = [board.board[r + i][c] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        stats['my_threes'] += 1
                        threats_this_board += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        stats['opp_threes'] += 1
                        opp_threats_this_board += 1
            
            # Diagonal analysis
            for r in range(board.rows - 3):
                for c in range(board.cols - 3):
                    window = [board.board[r + i][c + i] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        threats_this_board += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        opp_threats_this_board += 1
            
            for r in range(3, board.rows):
                for c in range(board.cols - 3):
                    window = [board.board[r - i][c + i] for i in range(4)]
                    if window.count(self.player) == 3 and window.count(0) == 1:
                        threats_this_board += 1
                    if window.count(opponent) == 3 and window.count(0) == 1:
                        opp_threats_this_board += 1
            
            # Double threat detection
            if threats_this_board >= 2:
                stats['my_double_threats'] += 1
            if opp_threats_this_board >= 2:
                stats['opp_double_threats'] += 1
            
            # Positional analysis
            for r in range(board.rows):
                for c in range(board.cols):
                    if board.board[r][c] == self.player:
                        if c == center_col:
                            stats['center_control'] += 1
                        elif c in [center_col - 1, center_col + 1]:
                            stats['adjacent_control'] += 1
                        if r == board.rows - 1:
                            stats['bottom_control'] += 1
                        if c == 0 or c == board.cols - 1:
                            stats['edge_pieces'] += 1
                        if r < 2:  # Top two rows
                            stats['high_pieces'] += 1
                    elif board.board[r][c] == opponent:
                        if c == center_col:
                            stats['center_control'] -= 1
                        elif c in [center_col - 1, center_col + 1]:
                            stats['adjacent_control'] -= 1
            
            stats['avg_mobility'] += len(board.getValidMoves())
        
        stats['avg_mobility'] /= len(critical_boards)
        
        # adjust weights based on game result and stats
        
        if self.last_game_result == 1:  # WIN
            # boost good moves
            if stats['my_threes'] > stats['opp_threes']:
                self.weights['three'] *= (1 + lr)
            if stats['my_twos'] > stats['opp_twos']:
                self.weights['two'] *= (1 + lr * 0.7)
            if stats['my_open_twos'] > 0:
                self.weights['two_open'] *= (1 + lr)
            if stats['my_double_threats'] > 0:
                self.weights['double_threat'] *= (1 + lr)
                self.weights['trap_setup'] *= (1 + lr * 0.5)
            if stats['center_control'] > 0:
                self.weights['center'] *= (1 + lr * 0.5)
                self.weights['center_adjacent'] *= (1 + lr * 0.3)
            if stats['bottom_control'] > 0:
                self.weights['bottom_row'] *= (1 + lr * 0.3)
            
            # do not over-defend when wining
            self.weights['opp_three'] *= (1 - lr * 0.2)
            self.weights['opp_two'] *= (1 - lr * 0.2)
            
        elif self.last_game_result == -1:  # LOSS
            # boost defense
            self.weights['opp_three'] *= (1 + lr * 1.2)
            self.weights['opp_two'] *= (1 + lr * 0.8)
            if stats['opp_open_twos'] > stats['my_open_twos']:
                self.weights['opp_two_open'] *= (1 + lr)
            if stats['opp_double_threats'] > stats['my_double_threats']:
                self.weights['double_threat'] *= (1 + lr * 0.5)
            
            # also boost offense - passive play loses
            if stats['my_threes'] < stats['opp_threes']:
                self.weights['three'] *= (1 + lr * 0.5)
            if stats['center_control'] < 0:
                self.weights['center'] *= (1 + lr * 0.7)
                self.weights['center_adjacent'] *= (1 + lr * 0.5)
            
            # adjust positional play
            if stats['edge_pieces'] > 3:
                self.weights['edge_penalty'] *= (1 + lr * 0.5)  # More penalty
            if stats['high_pieces'] > 3:
                self.weights['height_penalty'] *= (1 + lr * 0.3)
            
            # maintain more choices
            self.weights['mobility'] *= (1 + lr * 0.3)
            
        else:  # draw
            # Small adjustments toward more aggressive play
            self.weights['three'] *= (1 + lr * 0.2)
            self.weights['threat_count'] *= (1 + lr * 0.1)
        
        # pull weights gently toward defaults
        defaults = {
            'three': 100, 'two': 15, 'two_open': 25, 'one_potential': 3,
            'opp_three': -120, 'opp_two': -20, 'opp_two_open': -35,
            'center': 5, 'center_adjacent': 3, 'bottom_row': 4,
            'height_penalty': -2, 'double_threat': 80, 'blocked_three': -10,
            'trap_setup': 40, 'mobility': 2, 'threat_count': 15,
            'opp_threat_count': -20, 'edge_penalty': -1
        }
        decay = 0.02  # gently pull toward defaults
        for key in self.weights:
            if key in defaults:
                self.weights[key] = self.weights[key] * (1 - decay) + defaults[key] * decay
        
        result_str = "WIN" if self.last_game_result == 1 else "LOSS" if self.last_game_result == -1 else "DRAW"
        print(f"{result_str} | my_3s:{stats['my_threes']} opp_3s:{stats['opp_threes']} center:{stats['center_control']:+d} dbl_threats:{stats['my_double_threats']}/{stats['opp_double_threats']}")
        print(f"  → three={self.weights['three']:.0f}, opp_three={self.weights['opp_three']:.0f}, dbl_threat={self.weights['double_threat']:.0f}")


    def save_weights(self):
        with open(_WEIGHTS_FILE, 'w') as f:
            json.dump(self.weights, f, indent=2)

    def load_weights(self):
        # Store defaults to merge with loaded weights
        default_weights = self.weights.copy()
        try:
            with open(_WEIGHTS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge: use loaded values where available, keep defaults for new keys
                for key in default_weights:
                    if key in loaded:
                        self.weights[key] = loaded[key]
                print(f"Loaded weights: {len(loaded)} keys found, {len(default_weights)} total keys")
        except FileNotFoundError:
            print("No saved weights found, using defaults")  
