import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from minimax_agent import MinimaxAgent
from adaptive_minimax import EvolvingMinimaxAgent
from board import Board


class Connect4Game:
    """Game logic wrapper that's compatible with both GUI and agents"""
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.turn = 1
        self.gameOver = False

    def dropPiece(self, col):
        if self.gameOver or col < 0 or col >= self.cols:
            return None, None
        
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                winCells = self._checkWin(row, col)
                if winCells:
                    self.gameOver = True
                    return "WIN", winCells
                if self._isDraw():
                    self.gameOver = True
                    return "DRAW", None
                self.turn = 3 - self.turn
                return "OK", None
        return None, None

    def _checkWin(self, row, col):
        player = self.board[row][col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            cells = [(row, col)]
            for sign in [1, -1]:
                for i in range(1, 4):
                    r, c = row + dr * i * sign, col + dc * i * sign
                    if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                        cells.append((r, c))
                    else:
                        break
            if len(cells) >= 4:
                return cells
        return None

    def _isDraw(self):
        return all(self.board[0][c] != 0 for c in range(self.cols))

    def getValidMoves(self):
        return [c for c in range(self.cols) if self.board[0][c] == 0]

    def checkWinState(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 0 and self._checkWin(r, c):
                    return self.board[r][c]
        return 0

    def checkDrawState(self):
        return self._isDraw() and self.checkWinState() == 0

    def copy(self):
        newGame = Connect4Game()
        newGame.board = [row[:] for row in self.board]
        newGame.turn = self.turn
        newGame.gameOver = self.gameOver
        return newGame

    def reset(self):
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.turn = 1
        self.gameOver = False


class connect4Gui:
    aiDelay = 500
    
    colors = {
        'bgDark': '#1a1a2e',
        'bgPanel': '#16213e',
        'boardBg': '#0f3460',
        'slotEmpty': '#1a1a2e',
        'p1': '#e94560',
        'p1Light': '#ff6b6b',
        'p2': '#f1c40f',
        'p2Light': '#f39c12',
        'text': '#ffffff',
        'textDim': '#a0a0a0',
        'accent': '#3498db',
        'success': '#2ecc71',
        'border': '#4a4a6a',
        'btnText': '#ffffff',
    }

    def __init__(self, root, on_back=None):
        self.root = root
        self.on_back = on_back
        self.root.title("Connect 4")
        
        self.root.attributes('-fullscreen', True) 
        self.root.configure(bg=self.colors['bgDark'])
        
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', 
                                                               not self.root.attributes('-fullscreen')))
        
        self.root.update_idletasks()
        self.screenW = self.root.winfo_screenwidth()
        self.screenH = self.root.winfo_screenheight()
        
        availableH = self.screenH - 180
        availableW = self.screenW - 100
        self.cellSize = min(availableW // 7, availableH // 6, 100)
        self.radius = int(self.cellSize * 0.40)
        self.boardW = 7 * self.cellSize
        self.boardH = 6 * self.cellSize
        
        self.game = Connect4Game()
        self.players = [None, None]
        self.winningCells = []
        self.hoverCol = -1
        self.isAiThinking = False
        
        self.playerTypes = ["Human", "Minimax", "Evolving"]
        
        self._createMenuScreen()
        self._createGameScreen()
        
        self.showMenu()

    def _createMenuScreen(self):
        self.menuFrame = tk.Frame(self.root, bg=self.colors['bgDark'])
        
        center = tk.Frame(self.menuFrame, bg=self.colors['bgDark'])
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center, text="CONNECT", font=('Helvetica Neue', 72, 'bold'),
                bg=self.colors['bgDark'], fg=self.colors['p1']).pack()
        tk.Label(center, text="FOUR", font=('Helvetica Neue', 72, 'bold'),
                bg=self.colors['bgDark'], fg=self.colors['p2']).pack()
        
        tk.Frame(center, height=60, bg=self.colors['bgDark']).pack()
        
        panel = tk.Frame(center, bg=self.colors['bgPanel'], padx=40, pady=30)
        panel.pack()
        
        p1Frame = tk.Frame(panel, bg=self.colors['bgPanel'])
        p1Frame.pack(pady=15)
        
        tk.Label(p1Frame, text="● PLAYER 1", font=('Helvetica', 18, 'bold'),
                bg=self.colors['bgPanel'], fg=self.colors['p1']).pack(anchor='w')
        
        self.p1Var = tk.StringVar(value="Human")
        self.p1Var.trace_add('write', self._onP1Change)
        p1Menu = ttk.Combobox(p1Frame, textvariable=self.p1Var, values=self.playerTypes,
                              state='readonly', width=20, font=('Helvetica', 14))
        p1Menu.pack(pady=5)
        
        self.p1DiffFrame = tk.Frame(p1Frame, bg=self.colors['bgPanel'])
        tk.Label(self.p1DiffFrame, text="Difficulty:", font=('Helvetica', 12),
                bg=self.colors['bgPanel'], fg=self.colors['textDim']).pack(side='left')
        self.p1Diff = tk.StringVar(value="medium")
        ttk.Combobox(self.p1DiffFrame, textvariable=self.p1Diff, values=["easy", "medium", "hard"],
                    state='readonly', width=10, font=('Helvetica', 12)).pack(side='left', padx=5)
        
        tk.Frame(panel, height=2, bg=self.colors['border']).pack(fill='x', pady=15)
        
        p2Frame = tk.Frame(panel, bg=self.colors['bgPanel'])
        p2Frame.pack(pady=15)
        
        tk.Label(p2Frame, text="● PLAYER 2", font=('Helvetica', 18, 'bold'),
                bg=self.colors['bgPanel'], fg=self.colors['p2']).pack(anchor='w')
        
        self.p2Var = tk.StringVar(value="Human")
        self.p2Var.trace_add('write', self._onP2Change)
        p2Menu = ttk.Combobox(p2Frame, textvariable=self.p2Var, values=self.playerTypes,
                              state='readonly', width=20, font=('Helvetica', 14))
        p2Menu.pack(pady=5)
        
        self.p2DiffFrame = tk.Frame(p2Frame, bg=self.colors['bgPanel'])
        tk.Label(self.p2DiffFrame, text="Difficulty:", font=('Helvetica', 12),
                bg=self.colors['bgPanel'], fg=self.colors['textDim']).pack(side='left')
        self.p2Diff = tk.StringVar(value="medium")
        ttk.Combobox(self.p2DiffFrame, textvariable=self.p2Diff, values=["easy", "medium", "hard"],
                    state='readonly', width=10, font=('Helvetica', 12)).pack(side='left', padx=5)
        
        tk.Frame(center, height=40, bg=self.colors['bgDark']).pack()
        
        btnFrame = tk.Frame(center, bg=self.colors['bgDark'])
        btnFrame.pack()
        
        self._createButton(btnFrame, "START GAME", '#1e8449', self._startGame).pack(side='left', padx=10)
        if self.on_back:
            self._createButton(btnFrame, "BACK", '#922b21', self.go_back).pack(side='left', padx=10)
        else:
            self._createButton(btnFrame, "QUIT", '#922b21', self.root.destroy).pack(side='left', padx=10)
        
        tk.Label(center, text="Press ESC to exit fullscreen • F11 to toggle",
                font=('Helvetica', 11), bg=self.colors['bgDark'], 
                fg=self.colors['textDim']).pack(pady=(40, 0))

    def _createButton(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=('Helvetica', 18, 'bold'),
                       bg=color, fg="#000000",
                       activebackground=self._lighten(color),
                       activeforeground='#ffffff', relief='solid', bd=2,
                       padx=35, pady=15, cursor='hand2', command=command,
                       highlightthickness=2, highlightbackground='#ffffff')
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._lighten(color)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=color))
        return btn

    def _lighten(self, hexColor):
        r = int(hexColor[1:3], 16)
        g = int(hexColor[3:5], 16)
        b = int(hexColor[5:7], 16)
        factor = 1.2
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _onP1Change(self, *args):
        if self.p1Var.get() == "Minimax":
            self.p1DiffFrame.pack(pady=5)
        else:
            self.p1DiffFrame.pack_forget()

    def _onP2Change(self, *args):
        if self.p2Var.get() == "Minimax":
            self.p2DiffFrame.pack(pady=5)
        else:
            self.p2DiffFrame.pack_forget()

    def _createGameScreen(self):
        self.gameFrame = tk.Frame(self.root, bg=self.colors['bgDark'])
        
        self.canvas = tk.Canvas(self.gameFrame, width=self.screenW, height=self.screenH,
                               bg=self.colors['bgDark'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.canvas.bind('<Button-1>', self._onClick)
        self.canvas.bind('<Motion>', self._onMotion)

    def showMenu(self):
        self.gameFrame.pack_forget()
        self.menuFrame.pack(fill='both', expand=True)

    def showGame(self):
        self.menuFrame.pack_forget()
        self.gameFrame.pack(fill='both', expand=True)

    def _startGame(self):
        self.game.reset()
        self.winningCells = []
        self.hoverCol = -1
        self.isAiThinking = False
        
        p1Type = self.p1Var.get()
        if p1Type == "Human":
            self.players[0] = "Human"
        elif p1Type == "Minimax":
            self.players[0] = MinimaxAgent(player=1, difficulty=self.p1Diff.get())
        elif p1Type == "Evolving":
            self.players[0] = EvolvingMinimaxAgent(player=1)
        
        p2Type = self.p2Var.get()
        if p2Type == "Human":
            self.players[1] = "Human"
        elif p2Type == "Minimax":
            self.players[1] = MinimaxAgent(player=2, difficulty=self.p2Diff.get())
        elif p2Type == "Evolving":
            self.players[1] = EvolvingMinimaxAgent(player=2)
        
        self.showGame()
        self._draw()
        
        if self.players[0] != "Human":
            self.root.after(self.aiDelay, self._aiMove)

    def _draw(self):
        self.canvas.delete('all')
        
        bx = (self.screenW - self.boardW) // 2
        by = 100
        
        self._drawHeader(50)
        
        pad = 15
        self.canvas.create_rectangle(bx - pad, by - pad, 
                                     bx + self.boardW + pad, by + self.boardH + pad,
                                     fill=self.colors['boardBg'], outline='', width=0)
        
        for r in range(6):
            for c in range(7):
                cx = bx + c * self.cellSize + self.cellSize // 2
                cy = by + r * self.cellSize + self.cellSize // 2
                
                val = self.game.board[r][c]
                if val == 1:
                    fill = self.colors['p1']
                elif val == 2:
                    fill = self.colors['p2']
                else:
                    fill = self.colors['slotEmpty']
                
                outlineColor = fill
                outlineWidth = 0
                if self.winningCells and (r, c) in self.winningCells:
                    outlineColor = 'white'
                    outlineWidth = 4
                
                self.canvas.create_oval(cx - self.radius, cy - self.radius,
                                       cx + self.radius, cy + self.radius,
                                       fill=fill, outline=outlineColor, width=outlineWidth)
        
        if not self.game.gameOver and self._isHumanTurn() and 0 <= self.hoverCol < 7:
            targetRow = self._getDropRow(self.hoverCol)
            if targetRow >= 0:
                cx = bx + self.hoverCol * self.cellSize + self.cellSize // 2
                cy = by + targetRow * self.cellSize + self.cellSize // 2
                color = self.colors['p1'] if self.game.turn == 1 else self.colors['p2']
                self.canvas.create_oval(cx - self.radius, cy - self.radius,
                                       cx + self.radius, cy + self.radius,
                                       fill=color, outline=color, width=0, stipple='gray50')
                arrowY = by - 15
                self.canvas.create_polygon(cx, arrowY, cx - 10, arrowY - 15, cx + 10, arrowY - 15,
                                          fill=color, outline='')
        
        self._drawFooter(by + self.boardH + 30)

    def _drawHeader(self, y):
        if self.game.gameOver:
            if self.winningCells:
                winner = self.game.board[self.winningCells[0][0]][self.winningCells[0][1]]
                color = self.colors['p1'] if winner == 1 else self.colors['p2']
                text = f"PLAYER {winner} WINS!"
            else:
                color = self.colors['text']
                text = "IT'S A DRAW!"
        else:
            color = self.colors['p1'] if self.game.turn == 1 else self.colors['p2']
            playerName = "Human" if self._isHumanTurn() else self._getAiName()
            text = f"PLAYER {self.game.turn}'s TURN" + (f" ({playerName})" if not self._isHumanTurn() else "")
            if self.isAiThinking:
                text = f"PLAYER {self.game.turn} THINKING..."
        
        self.canvas.create_text(self.screenW // 2 + 2, y + 2, text=text,
                               font=('Helvetica', 24, 'bold'), fill='#000000')
        self.canvas.create_text(self.screenW // 2, y, text=text,
                               font=('Helvetica', 24, 'bold'), fill=color)

    def _drawFooter(self, y):
        btnY = min(y, self.screenH - 70)
        self._drawBtn(self.screenW // 2 - 160, btnY, 150, 55, "NEW GAME", 
                      '#1a5276', 'new_game')
        self._drawBtn(self.screenW // 2 + 10, btnY, 150, 55, "MENU",
                      '#1e8449', 'menu')

    def _drawBtn(self, x, y, w, h, text, color, tag):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline='#ffffff', width=2, tags=tag)
        self.canvas.create_text(x + w // 2, y + h // 2, text=text,
                               font=('Helvetica', 18, 'bold'), fill='#ffffff', tags=tag)
        self.canvas.tag_bind(tag, '<Button-1>', lambda e: self._onBtnClick(tag))

    def _onBtnClick(self, tag):
        if tag == 'new_game':
            self._resetGame()
        elif tag == 'menu':
            self.showMenu()

    def _resetGame(self):
        if not self.game.gameOver and any(isinstance(p, EvolvingMinimaxAgent) for p in self.players):
            for p in self.players:
                if isinstance(p, EvolvingMinimaxAgent):
                    p.last_game_boards = []
        
        self.game.reset()
        self.winningCells = []
        self.hoverCol = -1
        self.isAiThinking = False
        self._draw()
        
        if self.players[0] != "Human":
            self.root.after(self.aiDelay, self._aiMove)

    def _isHumanTurn(self):
        return self.players[self.game.turn - 1] == "Human"

    def _getAiName(self):
        player = self.players[self.game.turn - 1]
        if isinstance(player, EvolvingMinimaxAgent):
            return "Evolving AI"
        elif isinstance(player, MinimaxAgent):
            return "Minimax AI"
        return "AI"

    def _getDropRow(self, col):
        for r in range(5, -1, -1):
            if self.game.board[r][col] == 0:
                return r
        return -1

    def _onClick(self, event):
        if self.game.gameOver or not self._isHumanTurn() or self.isAiThinking:
            return
        
        bx = (self.screenW - self.boardW) // 2
        by = 100
        
        if bx <= event.x <= bx + self.boardW and by <= event.y <= by + self.boardH:
            col = (event.x - bx) // self.cellSize
            self._makeMove(col)

    def _onMotion(self, event):
        if self.game.gameOver or not self._isHumanTurn():
            if self.hoverCol != -1:
                self.hoverCol = -1
                self._draw()
            return
        
        bx = (self.screenW - self.boardW) // 2
        
        if bx <= event.x <= bx + self.boardW:
            newCol = (event.x - bx) // self.cellSize
            newCol = max(0, min(6, newCol))
        else:
            newCol = -1
        
        if newCol != self.hoverCol:
            self.hoverCol = newCol
            self._draw()

    def _makeMove(self, col):
        if col < 0 or col > 6:
            return
        
        for p in self.players:
            if isinstance(p, EvolvingMinimaxAgent):
                p.record_game_state(self.game)
        
        result, winCells = self.game.dropPiece(col)
        
        if result is None:
            return
        
        if result == "WIN":
            self.winningCells = winCells
            self._draw()
            self._finalizeGame()
        elif result == "DRAW":
            self._draw()
            self._finalizeGame()
        else:
            self._draw()
            if not self._isHumanTurn():
                self.root.after(self.aiDelay, self._aiMove)

    def _aiMove(self):
        if self.game.gameOver:
            return
        
        self.isAiThinking = True
        self._draw()
        self.root.update()
        
        player = self.players[self.game.turn - 1]
        move = player.get_move(self.game)
        
        self.isAiThinking = False
        self._makeMove(move)

    def _finalizeGame(self):
        for p in self.players:
            if isinstance(p, EvolvingMinimaxAgent):
                p.finalize_game(self.game)
        print("Game finished - Evolving agents updated their weights")

    def go_back(self):
        if hasattr(self, 'menuFrame') and self.menuFrame:
            self.menuFrame.destroy()
        if hasattr(self, 'gameFrame') and self.gameFrame:
            self.gameFrame.destroy()
        if self.on_back:
            self.on_back()


if __name__ == "__main__":
    root = tk.Tk()
    app = connect4Gui(root)
    root.mainloop()
