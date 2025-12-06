"""
Connect 4 GUI - Modern Fullscreen Design
Features:
- Fullscreen on launch
- 0.5s AI thinking delay for UX
- Adaptive Minimax learning integration
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add src directory to path for imports
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
        self.game_over = False

    def drop_piece(self, col):
        if self.game_over or col < 0 or col >= self.cols:
            return None, None
        
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                win_cells = self._check_win(row, col)
                if win_cells:
                    self.game_over = True
                    return "WIN", win_cells
                if self._is_draw():
                    self.game_over = True
                    return "DRAW", None
                self.turn = 3 - self.turn
                return "OK", None
        return None, None

    def _check_win(self, row, col):
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

    def _is_draw(self):
        return all(self.board[0][c] != 0 for c in range(self.cols))

    def getValidMoves(self):
        return [c for c in range(self.cols) if self.board[0][c] == 0]

    def checkWinState(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 0 and self._check_win(r, c):
                    return self.board[r][c]
        return 0

    def checkDrawState(self):
        return self._is_draw() and self.checkWinState() == 0

    def copy(self):
        new_game = Connect4Game()
        new_game.board = [row[:] for row in self.board]
        new_game.turn = self.turn
        new_game.game_over = self.game_over
        return new_game

    def reset(self):
        self.board = [[0] * self.cols for _ in range(self.rows)]
        self.turn = 1
        self.game_over = False


class Connect4GUI:
    # Constants
    AI_DELAY = 500  # 0.5 seconds delay for AI moves
    
    # Color Scheme - High Contrast Dark Theme
    COLORS = {
        'bg_dark': '#1a1a2e',       # Deep navy background
        'bg_panel': '#16213e',      # Panel background
        'board_bg': '#0f3460',      # Board frame - darker blue
        'slot_empty': '#1a1a2e',    # Empty slots - very dark
        'p1': '#e94560',            # Bright Red
        'p1_light': '#ff6b6b',
        'p2': '#f1c40f',            # Bright Yellow
        'p2_light': '#f39c12',
        'text': '#ffffff',          # Pure white for maximum readability
        'text_dim': '#a0a0a0',      # Light gray
        'accent': '#3498db',        # Bright blue for buttons
        'success': '#2ecc71',       # Bright green
        'border': '#4a4a6a',
        'btn_text': '#ffffff',      # White button text
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4")
        
        # Fullscreen immediately
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Escape to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', 
                                                               not self.root.attributes('-fullscreen')))
        
        # Get screen dimensions
        self.root.update_idletasks()
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        # Calculate board dimensions (responsive - ensure fits on screen)
        # Leave room for header (100px) and footer (80px)
        available_h = self.screen_h - 180
        available_w = self.screen_w - 100
        self.cell_size = min(available_w // 7, available_h // 6, 100)  # Cap at 100px
        self.radius = int(self.cell_size * 0.40)
        self.board_w = 7 * self.cell_size
        self.board_h = 6 * self.cell_size
        
        # Game state
        self.game = Connect4Game()
        self.players = [None, None]
        self.winning_cells = []
        self.hover_col = -1
        self.is_ai_thinking = False
        
        # Player type options
        self.player_types = ["Human", "Minimax", "Evolving"]
        
        # Create frames
        self._create_menu_screen()
        self._create_game_screen()
        
        # Start with menu
        self.show_menu()

    def _create_menu_screen(self):
        """Create the main menu screen"""
        self.menu_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        
        # Center container
        center = tk.Frame(self.menu_frame, bg=self.COLORS['bg_dark'])
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(center, text="CONNECT", font=('Helvetica Neue', 72, 'bold'),
                bg=self.COLORS['bg_dark'], fg=self.COLORS['p1']).pack()
        tk.Label(center, text="FOUR", font=('Helvetica Neue', 72, 'bold'),
                bg=self.COLORS['bg_dark'], fg=self.COLORS['p2']).pack()
        
        # Spacer
        tk.Frame(center, height=60, bg=self.COLORS['bg_dark']).pack()
        
        # Player Selection Panel
        panel = tk.Frame(center, bg=self.COLORS['bg_panel'], padx=40, pady=30)
        panel.pack()
        
        # Player 1
        p1_frame = tk.Frame(panel, bg=self.COLORS['bg_panel'])
        p1_frame.pack(pady=15)
        
        tk.Label(p1_frame, text="● PLAYER 1", font=('Helvetica', 18, 'bold'),
                bg=self.COLORS['bg_panel'], fg=self.COLORS['p1']).pack(anchor='w')
        
        self.p1_var = tk.StringVar(value="Human")
        self.p1_var.trace_add('write', self._on_p1_change)
        p1_menu = ttk.Combobox(p1_frame, textvariable=self.p1_var, values=self.player_types,
                              state='readonly', width=20, font=('Helvetica', 14))
        p1_menu.pack(pady=5)
        
        self.p1_diff_frame = tk.Frame(p1_frame, bg=self.COLORS['bg_panel'])
        tk.Label(self.p1_diff_frame, text="Difficulty:", font=('Helvetica', 12),
                bg=self.COLORS['bg_panel'], fg=self.COLORS['text_dim']).pack(side='left')
        self.p1_diff = tk.StringVar(value="medium")
        ttk.Combobox(self.p1_diff_frame, textvariable=self.p1_diff, values=["easy", "medium", "hard"],
                    state='readonly', width=10, font=('Helvetica', 12)).pack(side='left', padx=5)
        
        # Separator
        tk.Frame(panel, height=2, bg=self.COLORS['border']).pack(fill='x', pady=15)
        
        # Player 2
        p2_frame = tk.Frame(panel, bg=self.COLORS['bg_panel'])
        p2_frame.pack(pady=15)
        
        tk.Label(p2_frame, text="● PLAYER 2", font=('Helvetica', 18, 'bold'),
                bg=self.COLORS['bg_panel'], fg=self.COLORS['p2']).pack(anchor='w')
        
        self.p2_var = tk.StringVar(value="Human")
        self.p2_var.trace_add('write', self._on_p2_change)
        p2_menu = ttk.Combobox(p2_frame, textvariable=self.p2_var, values=self.player_types,
                              state='readonly', width=20, font=('Helvetica', 14))
        p2_menu.pack(pady=5)
        
        self.p2_diff_frame = tk.Frame(p2_frame, bg=self.COLORS['bg_panel'])
        tk.Label(self.p2_diff_frame, text="Difficulty:", font=('Helvetica', 12),
                bg=self.COLORS['bg_panel'], fg=self.COLORS['text_dim']).pack(side='left')
        self.p2_diff = tk.StringVar(value="medium")
        ttk.Combobox(self.p2_diff_frame, textvariable=self.p2_diff, values=["easy", "medium", "hard"],
                    state='readonly', width=10, font=('Helvetica', 12)).pack(side='left', padx=5)
        
        # Spacer
        tk.Frame(center, height=40, bg=self.COLORS['bg_dark']).pack()
        
        # Buttons - using darker colors for clear white text
        btn_frame = tk.Frame(center, bg=self.COLORS['bg_dark'])
        btn_frame.pack()
        
        self._create_button(btn_frame, "START GAME", '#1e8449', self._start_game).pack(side='left', padx=10)  # Dark green
        self._create_button(btn_frame, "QUIT", '#922b21', self.root.destroy).pack(side='left', padx=10)  # Dark red
        
        # Footer
        tk.Label(center, text="Press ESC to exit fullscreen • F11 to toggle",
                font=('Helvetica', 11), bg=self.COLORS['bg_dark'], 
                fg=self.COLORS['text_dim']).pack(pady=(40, 0))

    def _create_button(self, parent, text, color, command):
        """Create a styled button with high contrast"""
        btn = tk.Button(parent, text=text, font=('Helvetica', 18, 'bold'),
                       bg=color, fg="#000000",  # Black text always
                       activebackground=self._lighten(color),
                       activeforeground='#ffffff', relief='solid', bd=2,
                       padx=35, pady=15, cursor='hand2', command=command,
                       highlightthickness=2, highlightbackground='#ffffff')
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._lighten(color)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=color))
        return btn

    def _lighten(self, hex_color):
        """Lighten a hex color"""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        factor = 1.2
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _on_p1_change(self, *args):
        if self.p1_var.get() == "Minimax":
            self.p1_diff_frame.pack(pady=5)
        else:
            self.p1_diff_frame.pack_forget()

    def _on_p2_change(self, *args):
        if self.p2_var.get() == "Minimax":
            self.p2_diff_frame.pack(pady=5)
        else:
            self.p2_diff_frame.pack_forget()

    def _create_game_screen(self):
        """Create the game screen with canvas"""
        self.game_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        
        self.canvas = tk.Canvas(self.game_frame, width=self.screen_w, height=self.screen_h,
                               bg=self.COLORS['bg_dark'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<Motion>', self._on_motion)

    def show_menu(self):
        """Show the menu screen"""
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill='both', expand=True)

    def show_game(self):
        """Show the game screen"""
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill='both', expand=True)

    def _start_game(self):
        """Initialize and start a new game"""
        self.game.reset()
        self.winning_cells = []
        self.hover_col = -1
        self.is_ai_thinking = False
        
        # Create player instances
        p1_type = self.p1_var.get()
        if p1_type == "Human":
            self.players[0] = "Human"
        elif p1_type == "Minimax":
            self.players[0] = MinimaxAgent(player=1, difficulty=self.p1_diff.get())
        elif p1_type == "Evolving":
            self.players[0] = EvolvingMinimaxAgent(player=1)
        
        p2_type = self.p2_var.get()
        if p2_type == "Human":
            self.players[1] = "Human"
        elif p2_type == "Minimax":
            self.players[1] = MinimaxAgent(player=2, difficulty=self.p2_diff.get())
        elif p2_type == "Evolving":
            self.players[1] = EvolvingMinimaxAgent(player=2)
        
        self.show_game()
        self._draw()
        
        # If first player is AI, start their move
        if self.players[0] != "Human":
            self.root.after(self.AI_DELAY, self._ai_move)

    def _draw(self):
        """Render the entire game board"""
        self.canvas.delete('all')
        
        # Calculate board position (centered, with room for header/footer)
        bx = (self.screen_w - self.board_w) // 2
        by = 100  # Fixed top margin for header
        
        # Header
        self._draw_header(50)
        
        # Board background with rounded corners (simulated)
        pad = 15
        self.canvas.create_rectangle(bx - pad, by - pad, 
                                     bx + self.board_w + pad, by + self.board_h + pad,
                                     fill=self.COLORS['board_bg'], outline='', width=0)
        
        # Draw cells
        for r in range(6):
            for c in range(7):
                cx = bx + c * self.cell_size + self.cell_size // 2
                cy = by + r * self.cell_size + self.cell_size // 2
                
                val = self.game.board[r][c]
                if val == 1:
                    fill = self.COLORS['p1']
                elif val == 2:
                    fill = self.COLORS['p2']
                else:
                    fill = self.COLORS['slot_empty']
                
                # Check for winning highlight
                outline_color = fill
                outline_width = 0
                if self.winning_cells and (r, c) in self.winning_cells:
                    outline_color = 'white'
                    outline_width = 4
                
                self.canvas.create_oval(cx - self.radius, cy - self.radius,
                                       cx + self.radius, cy + self.radius,
                                       fill=fill, outline=outline_color, width=outline_width)
        
        # Ghost piece (hover preview)
        if not self.game.game_over and self._is_human_turn() and 0 <= self.hover_col < 7:
            target_row = self._get_drop_row(self.hover_col)
            if target_row >= 0:
                cx = bx + self.hover_col * self.cell_size + self.cell_size // 2
                cy = by + target_row * self.cell_size + self.cell_size // 2
                color = self.COLORS['p1'] if self.game.turn == 1 else self.COLORS['p2']
                self.canvas.create_oval(cx - self.radius, cy - self.radius,
                                       cx + self.radius, cy + self.radius,
                                       fill=color, outline=color, width=0, stipple='gray50')
                # Drop indicator arrow above board
                arrow_y = by - 15
                self.canvas.create_polygon(cx, arrow_y, cx - 10, arrow_y - 15, cx + 10, arrow_y - 15,
                                          fill=color, outline='')
        
        # Footer buttons - positioned below board with margin
        self._draw_footer(by + self.board_h + 30)

    def _draw_header(self, y):
        """Draw the header with turn indicator"""
        if self.game.game_over:
            if self.winning_cells:
                winner = self.game.board[self.winning_cells[0][0]][self.winning_cells[0][1]]
                color = self.COLORS['p1'] if winner == 1 else self.COLORS['p2']
                text = f"PLAYER {winner} WINS!"
            else:
                color = self.COLORS['text']
                text = "IT'S A DRAW!"
        else:
            color = self.COLORS['p1'] if self.game.turn == 1 else self.COLORS['p2']
            player_name = "Human" if self._is_human_turn() else self._get_ai_name()
            text = f"PLAYER {self.game.turn}'s TURN" + (f" ({player_name})" if not self._is_human_turn() else "")
            if self.is_ai_thinking:
                text = f"PLAYER {self.game.turn} THINKING..."
        
        # Draw with shadow for better visibility
        self.canvas.create_text(self.screen_w // 2 + 2, y + 2, text=text,
                               font=('Helvetica', 24, 'bold'), fill='#000000')  # Shadow
        self.canvas.create_text(self.screen_w // 2, y, text=text,
                               font=('Helvetica', 24, 'bold'), fill=color)

    def _draw_footer(self, y):
        """Draw footer buttons"""
        # Ensure buttons are visible within screen
        btn_y = min(y, self.screen_h - 70)
        # New Game button - darker blue for contrast
        self._draw_btn(self.screen_w // 2 - 160, btn_y, 150, 55, "NEW GAME", 
                      '#1a5276', 'new_game')
        # Menu button - darker green for contrast
        self._draw_btn(self.screen_w // 2 + 10, btn_y, 150, 55, "MENU",
                      '#1e8449', 'menu')

    def _draw_btn(self, x, y, w, h, text, color, tag):
        """Draw a clickable button on canvas with clear text"""
        # Button background - darker color
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline='#ffffff', width=2, tags=tag)
        # Button text - LARGE white text for maximum visibility
        self.canvas.create_text(x + w // 2, y + h // 2, text=text,
                               font=('Helvetica', 18, 'bold'), fill='#ffffff', tags=tag)
        self.canvas.tag_bind(tag, '<Button-1>', lambda e: self._on_btn_click(tag))

    def _on_btn_click(self, tag):
        """Handle button clicks"""
        if tag == 'new_game':
            self._reset_game()
        elif tag == 'menu':
            self.show_menu()

    def _reset_game(self):
        """Reset the current game"""
        # Finalize for learning agents if game was in progress
        if not self.game.game_over and any(isinstance(p, EvolvingMinimaxAgent) for p in self.players):
            for p in self.players:
                if isinstance(p, EvolvingMinimaxAgent):
                    p.last_game_boards = []  # Clear without learning
        
        self.game.reset()
        self.winning_cells = []
        self.hover_col = -1
        self.is_ai_thinking = False
        self._draw()
        
        if self.players[0] != "Human":
            self.root.after(self.AI_DELAY, self._ai_move)

    def _is_human_turn(self):
        """Check if current turn is human"""
        return self.players[self.game.turn - 1] == "Human"

    def _get_ai_name(self):
        """Get name of current AI player"""
        player = self.players[self.game.turn - 1]
        if isinstance(player, EvolvingMinimaxAgent):
            return "Evolving AI"
        elif isinstance(player, MinimaxAgent):
            return "Minimax AI"
        return "AI"

    def _get_drop_row(self, col):
        """Find the row where a piece would land in the given column"""
        for r in range(5, -1, -1):
            if self.game.board[r][col] == 0:
                return r
        return -1

    def _on_click(self, event):
        """Handle canvas clicks"""
        if self.game.game_over or not self._is_human_turn() or self.is_ai_thinking:
            return
        
        bx = (self.screen_w - self.board_w) // 2
        by = 100  # Match the fixed top margin
        
        if bx <= event.x <= bx + self.board_w and by <= event.y <= by + self.board_h:
            col = (event.x - bx) // self.cell_size
            self._make_move(col)

    def _on_motion(self, event):
        """Handle mouse motion for hover effect"""
        if self.game.game_over or not self._is_human_turn():
            if self.hover_col != -1:
                self.hover_col = -1
                self._draw()
            return
        
        bx = (self.screen_w - self.board_w) // 2
        
        if bx <= event.x <= bx + self.board_w:
            new_col = (event.x - bx) // self.cell_size
            new_col = max(0, min(6, new_col))
        else:
            new_col = -1
        
        if new_col != self.hover_col:
            self.hover_col = new_col
            self._draw()

    def _make_move(self, col):
        """Make a move and handle result"""
        if col < 0 or col > 6:
            return
        
        # Record state for evolving agents BEFORE the move
        for p in self.players:
            if isinstance(p, EvolvingMinimaxAgent):
                p.record_game_state(self.game)
        
        result, win_cells = self.game.drop_piece(col)
        
        if result is None:
            return  # Invalid move
        
        if result == "WIN":
            self.winning_cells = win_cells
            self._draw()
            self._finalize_game()
        elif result == "DRAW":
            self._draw()
            self._finalize_game()
        else:
            self._draw()
            # Next player's turn
            if not self._is_human_turn():
                self.root.after(self.AI_DELAY, self._ai_move)

    def _ai_move(self):
        """Execute AI move with delay for UX"""
        if self.game.game_over:
            return
        
        self.is_ai_thinking = True
        self._draw()
        self.root.update()
        
        player = self.players[self.game.turn - 1]
        move = player.get_move(self.game)
        
        self.is_ai_thinking = False
        self._make_move(move)

    def _finalize_game(self):
        """Call finalize_game on EvolvingMinimaxAgent players for learning"""
        for p in self.players:
            if isinstance(p, EvolvingMinimaxAgent):
                p.finalize_game(self.game)
        print("Game finished - Evolving agents updated their weights")


if __name__ == "__main__":
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()
