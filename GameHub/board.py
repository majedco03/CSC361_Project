#the game logic for connect 4
#initialize when the game start and manage the board state
class Board:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.turn = 1  # Player 1 starts
        self.gameOver = False
    

    #Checks the top row of the column if there is a piece then this move is invalid
    def isValidMove(self, col):
        return self.board[0][col] == 0
    
    #Check if the player won after dropping a piece
    def checkWin(self, row, col):
        player = self.board[row][col]
        # Check horizontal, vertical, and two diagonal directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # Check in the positive direction
            for i in range(1, 4):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    count += 1
                else:
                    break
            
            # Check in the negative direction
            for i in range(1, 4):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    count += 1
                else:
                    break
            
            if count >= 4:
                return True
        return False
    
    def checkDraw(self):
        return all(self.board[0][c] != 0 for c in range(self.cols))
    
    # function to drop a piece in the selected column
    def drop_piece(self, col):
        if self.gameOver:
            return False # the game is over, no more moves allowed
        if not self.isValidMove(col):
            return False #invalid move
        for row in range(0,6):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                if self.checkWin(row, col):
                    self.gameOver = True
                    return "WIN"
                if self.checkDraw():
                    self.gameOver = True
                    return "DRAW"
                self.turn = 3 - self.turn #switch player
                return True
    
    # reset the game
    def reset(self):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.turn = 1
        self.gameOver = False

    # copy the board state
    def copy(self):
        new_game = Board(self.rows, self.cols)
        new_game.board = [row[:] for row in self.board]
        new_game.turn = self.turn
        new_game.gameOver = self.gameOver
        return new_game
    
    # get all valid moves
    def getValidMoves(self):
        return [c for c in range(self.cols) if self.isValidMove(c)]
    
    def gameOverState(self):
        return self.gameOver
    
    def checkWinState(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 0 and self.checkWin(r, c):
                    return self.board[r][c]
        return 0  # No winner yet
    