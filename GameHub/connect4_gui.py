import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from minimax_agent import MinimaxAgent

class Connect4Game:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.turn = 1  # 1 for Player 1 (Red), 2 for Player 2 (Yellow)
        self.game_over = False

    def drop_piece(self, col):
        if self.game_over:
            return False, None
        
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = self.turn
                winning_pieces = self.check_win(row, col)
                if winning_pieces:
                    self.game_over = True
                    return "WIN", winning_pieces
                if self.check_draw():
                    self.game_over = True
                    return "DRAW", None
                self.turn = 3 - self.turn  # Switch player
                return True, None
        return False, None  # Column is full

    def check_win(self, row, col):
        player = self.board[row][col]
        
        # Directions: horizontal, vertical, diagonal /, diagonal \
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            winning_pieces = [(row, col)]
            # Check positive direction
            for i in range(1, 4):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    winning_pieces.append((r, c))
                else:
                    break
            # Check negative direction
            for i in range(1, 4):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    winning_pieces.append((r, c))
                else:
                    break
            
            if len(winning_pieces) >= 4:
                return winning_pieces
        return None

    def check_draw(self):
        return all(self.board[0][c] != 0 for c in range(self.cols))

    def getValidMoves(self):
        return [c for c in range(self.cols) if self.board[0][c] == 0]

    def checkWinState(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != 0 and self.check_win(r, c):
                    return self.board[r][c]
        return 0

    def checkDrawState(self):
        return self.check_draw()

    def copy(self):
        new_game = Connect4Game()
        new_game.board = [row[:] for row in self.board]
        new_game.turn = self.turn
        new_game.game_over = self.game_over
        return new_game

    def reset(self):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.turn = 1
        self.game_over = False

class Connect4GUI:
    def __init__(self, root, on_back=None):
        self.root = root
        self.on_back = on_back  # Callback to GameHub
        
        # Modern Color Palette
        self.colors = {
            'bg': "#1a1a2e",        # Dark Navy Background
            'board': "#16213e",     # Slightly lighter navy for board container
            'slot_empty': "#0f3460",# Dark Blue for empty slots
            'p1': "#e94560",        # Neon Red/Pink
            'p2': "#fcdab7",        # Soft Yellow/Beige
            'text': "#ffffff",      # White
            'accent': "#e94560",    # Accent color
            'button': "#0f3460",    # Button background
            'button_hover': "#16213e"
        }
        
        # Configure Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("TFrame", background=self.colors['bg'])
        self.style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['text'], font=('Helvetica', 16))
        self.style.configure("Header.TLabel", font=('Helvetica', 48, 'bold'), foreground=self.colors['accent'])
        self.style.configure("SubHeader.TLabel", font=('Helvetica', 24), foreground=self.colors['text'])
        
        self.style.configure("GameBtn.TButton", 
                           font=('Helvetica', 14, 'bold'), 
                           background=self.colors['button'], 
                           foreground=self.colors['text'],
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.map("GameBtn.TButton",
                     background=[('active', self.colors['button_hover'])],
                     foreground=[('active', self.colors['accent'])])
        
        self.style.configure("TMenubutton", 
                           background=self.colors['button'], 
                           foreground=self.colors['text'],
                           font=('Helvetica', 12))

        self.game = Connect4Game()
        
        # Screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Calculate responsive board size
        self.cell_size = int(min(self.screen_width * 0.8 / 7, self.screen_height * 0.7 / 6))
        self.radius = int(self.cell_size * 0.4)
        
        self.board_width = 7 * self.cell_size
        self.board_height = 6 * self.cell_size
        self.offset_x = (self.screen_width - self.board_width) // 2
        self.offset_y = (self.screen_height - self.board_height) // 2
        
        self.players = [None, None]
        self.player_types = ["Human", "Minimax", "RL", "ML"]
        
        # Main Container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(expand=True, fill='both')
        
        # Setup Frame (Menu)
        self.setup_frame = ttk.Frame(self.main_container)
        self.setup_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        self.create_setup_ui()
        
        # Game Frame
        self.game_frame = ttk.Frame(self.main_container)
        
        self.canvas = tk.Canvas(self.game_frame, 
                              width=self.screen_width, 
                              height=self.screen_height, 
                              bg=self.colors['bg'], 
                              highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_motion)
        
        self.hover_col = -1
        self.winning_pieces = []
        
        self.create_game_buttons()

    def create_setup_ui(self):
        # Title
        ttk.Label(self.setup_frame, text="CONNECT 4", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 50))
        
        # Player 1 Section
        p1_frame = tk.Frame(self.setup_frame, bg=self.colors['bg'], bd=2, relief='groove')
        p1_frame.grid(row=1, column=0, padx=20, pady=10, sticky='nsew')
        
        tk.Label(p1_frame, text="PLAYER 1 (RED)", font=('Helvetica', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['p1']).pack(pady=10)
        
        self.player1_var = tk.StringVar(value="Human")
        self.player1_var.trace('w', self.update_ui_state)
        p1_menu = ttk.OptionMenu(p1_frame, self.player1_var, "Human", *self.player_types)
        p1_menu.pack(pady=5, padx=20, fill='x')
        
        self.p1_diff_label = tk.Label(p1_frame, text="Difficulty", font=('Helvetica', 12), bg=self.colors['bg'], fg=self.colors['text'])
        self.p1_diff_label.pack(pady=(10,0))
        self.diff1_var = tk.StringVar(value="easy")
        self.p1_diff_menu = ttk.OptionMenu(p1_frame, self.diff1_var, "easy", "easy", "medium", "hard")
        self.p1_diff_menu.pack(pady=5, padx=20, fill='x')

        # Player 2 Section
        p2_frame = tk.Frame(self.setup_frame, bg=self.colors['bg'], bd=2, relief='groove')
        p2_frame.grid(row=1, column=1, padx=20, pady=10, sticky='nsew')
        
        tk.Label(p2_frame, text="PLAYER 2 (YELLOW)", font=('Helvetica', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['p2']).pack(pady=10)
        
        self.player2_var = tk.StringVar(value="Human")
        self.player2_var.trace('w', self.update_ui_state)
        p2_menu = ttk.OptionMenu(p2_frame, self.player2_var, "Human", *self.player_types)
        p2_menu.pack(pady=5, padx=20, fill='x')
        
        self.p2_diff_label = tk.Label(p2_frame, text="Difficulty", font=('Helvetica', 12), bg=self.colors['bg'], fg=self.colors['text'])
        self.p2_diff_label.pack(pady=(10,0))
        self.diff2_var = tk.StringVar(value="easy")
        self.p2_diff_menu = ttk.OptionMenu(p2_frame, self.diff2_var, "easy", "easy", "medium", "hard")
        self.p2_diff_menu.pack(pady=5, padx=20, fill='x')
        
        # Buttons
        btn_frame = ttk.Frame(self.setup_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=50)
        
        ttk.Button(btn_frame, text="START GAME", style="GameBtn.TButton", command=self.start_game).pack(side='left', padx=10, ipadx=20, ipady=10)
        
        # Updated: "BACK TO HUB" instead of Exit
        ttk.Button(btn_frame, text="BACK TO HUB", style="GameBtn.TButton", command=self.return_to_hub).pack(side='left', padx=10, ipadx=20, ipady=10)
        
        self.update_ui_state()

    def update_ui_state(self, *args):
        # Player 1
        if self.player1_var.get() == "Minimax":
            self.p1_diff_label.pack(pady=(10,0))
            self.p1_diff_menu.pack(pady=5, padx=20, fill='x')
        else:
            self.p1_diff_label.pack_forget()
            self.p1_diff_menu.pack_forget()
            
        # Player 2
        if self.player2_var.get() == "Minimax":
            self.p2_diff_label.pack(pady=(10,0))
            self.p2_diff_menu.pack(pady=5, padx=20, fill='x')
        else:
            self.p2_diff_label.pack_forget()
            self.p2_diff_menu.pack_forget()

    def create_game_buttons(self):
        self.reset_btn = tk.Button(self.game_frame, text="NEW GAME", font=('Helvetica', 14, 'bold'),
                                 bg=self.colors['button'], fg=self.colors['text'],
                                 activebackground=self.colors['button_hover'], activeforeground=self.colors['accent'],
                                 relief='flat', bd=0, cursor="hand2", command=self.reset_game)
        
        # Updated: "BACK TO HUB"
        self.menu_btn = tk.Button(self.game_frame, text="BACK TO HUB", font=('Helvetica', 14, 'bold'),
                                 bg=self.colors['button'], fg=self.colors['text'],
                                 activebackground=self.colors['button_hover'], activeforeground=self.colors['accent'],
                                 relief='flat', bd=0, cursor="hand2", command=self.return_to_hub)

    def return_to_hub(self):
        # New function: Destroys current frame and calls the callback
        self.main_container.destroy()
        if self.on_back:
            self.on_back()

    def start_game(self):
        # Create player instances
        p1_type = self.player1_var.get()
        if p1_type == "Human":
            self.players[0] = "Human"
        elif p1_type == "Minimax":
            self.players[0] = MinimaxAgent(player=1, difficulty=self.diff1_var.get())
        
        p2_type = self.player2_var.get()
        if p2_type == "Human":
            self.players[1] = "Human"
        elif p2_type == "Minimax":
            self.players[1] = MinimaxAgent(player=2, difficulty=self.diff2_var.get())
        
        self.setup_frame.place_forget()
        self.game_frame.pack(fill='both', expand=True)
        self.draw_board()
        
        if self.players[0] != "Human":
            self.root.after(500, self.make_ai_move)

    def make_ai_move(self):
        if self.game.game_over:
            return
        current_player = self.players[self.game.turn - 1]
        if current_player == "Human":
            return
            
        self.canvas.config(cursor="watch")
        self.root.update()
        
        move = current_player.get_move(self.game)
        
        self.canvas.config(cursor="")
        
        result, winning_pieces = self.game.drop_piece(move)
        if winning_pieces:
            self.winning_pieces = winning_pieces
            
        self.draw_board()
        if result == "WIN":
            winner_name = "Red" if self.game.turn == 1 else "Yellow"
            self.show_game_over(f"{winner_name} Wins!")
        elif result == "DRAW":
            self.show_game_over("It's a Draw!")
        else:
            self.after_move()

    def after_move(self):
        if self.game.game_over:
            return
        if self.players[self.game.turn - 1] != "Human":
            self.root.after(100, self.make_ai_move)

    def draw_board(self):
        self.canvas.delete("all")
        
        # Title
        self.canvas.create_text(self.screen_width//2, 60, text="CONNECT 4", fill=self.colors['text'], font=('Helvetica', 36, 'bold'))
        
        # Status
        turn_text = f"PLAYER {self.game.turn}'S TURN"
        turn_color = self.colors['p1'] if self.game.turn == 1 else self.colors['p2']
        self.canvas.create_text(self.screen_width//2, 120, text=turn_text, fill=turn_color, font=('Helvetica', 24, 'bold'))

        # Board Background
        self.canvas.create_rectangle(
            self.offset_x - 20, self.offset_y - 20,
            self.offset_x + self.board_width + 20, self.offset_y + self.board_height + 20,
            fill=self.colors['board'], outline=self.colors['board'], width=0
        )
        
        # Slots
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x_center = self.offset_x + c * self.cell_size + self.cell_size / 2
                y_center = self.offset_y + r * self.cell_size + self.cell_size / 2
                
                val = self.game.board[r][c]
                if val == 1:
                    color = self.colors['p1']
                    outline = self.colors['p1']
                elif val == 2:
                    color = self.colors['p2']
                    outline = self.colors['p2']
                else:
                    color = self.colors['slot_empty']
                    outline = self.colors['slot_empty']
                
                width = 2
                if hasattr(self, 'winning_pieces') and self.winning_pieces and (r, c) in self.winning_pieces:
                    outline = "#ffffff"
                    width = 5
                
                self.canvas.create_oval(
                    x_center - self.radius, y_center - self.radius,
                    x_center + self.radius, y_center + self.radius,
                    fill=color, outline=outline, width=width
                )
        
        # Hover Indicator
        if not self.game.game_over and self.players[self.game.turn - 1] == "Human" and hasattr(self, 'hover_col') and self.hover_col != -1:
            c = self.hover_col
            target_row = -1
            for r in range(self.game.rows - 1, -1, -1):
                if self.game.board[r][c] == 0:
                    target_row = r
                    break
            
            if target_row != -1:
                x_center = self.offset_x + c * self.cell_size + self.cell_size / 2
                y_center = self.offset_y + target_row * self.cell_size + self.cell_size / 2
                
                color = self.colors['p1'] if self.game.turn == 1 else self.colors['p2']
                
                self.canvas.create_oval(
                    x_center - self.radius, y_center - self.radius,
                    x_center + self.radius, y_center + self.radius,
                    fill=color, outline=color, width=2, stipple='gray50'
                )
                
                x_header = self.offset_x + c * self.cell_size + self.cell_size / 2
                y_header = self.offset_y - 30
                self.canvas.create_polygon(
                    x_header, y_header, 
                    x_header - 10, y_header - 15, 
                    x_header + 10, y_header - 15, 
                    fill=color, outline=color
                )

        # Buttons position
        btn_y = self.offset_y + self.board_height + 60
        self.reset_btn.place(x=self.screen_width//2 - 140, y=btn_y, width=120, height=50)
        self.menu_btn.place(x=self.screen_width//2 + 20, y=btn_y, width=120, height=50)

    def show_game_over(self, message):
        cx, cy = self.screen_width // 2, self.screen_height // 2
        self.canvas.create_rectangle(cx - 200, cy - 100, cx + 200, cy + 100, fill=self.colors['board'], outline=self.colors['accent'], width=3)
        self.canvas.create_text(cx, cy - 20, text=message, fill=self.colors['text'], font=('Helvetica', 32, 'bold'))
        self.canvas.create_text(cx, cy + 40, text="Click New Game or Back", fill=self.colors['text'], font=('Helvetica', 16))

    def handle_click(self, event):
        if self.game.game_over or self.players[self.game.turn - 1] != "Human":
            return
            
        if event.x < self.offset_x or event.x > self.offset_x + self.board_width:
            return
            
        col = (event.x - self.offset_x) // self.cell_size
        if 0 <= col < self.game.cols:
            result = self.game.drop_piece(col)
            self.draw_board()
            
            if result == "WIN":
                winner_name = "Red" if self.game.turn == 1 else "Yellow"
                self.show_game_over(f"{winner_name} Wins!")
            elif result == "DRAW":
                self.show_game_over("It's a Draw!")
            else:
                self.after_move()

    def handle_motion(self, event):
        if self.game.game_over or self.players[self.game.turn - 1] != "Human":
            return
            
        if event.x < self.offset_x or event.x > self.offset_x + self.board_width:
            new_col = -1
        else:
            new_col = (event.x - self.offset_x) // self.cell_size
            if not (0 <= new_col < self.game.cols):
                new_col = -1
        
        if new_col != self.hover_col:
            self.hover_col = new_col
            self.draw_board()

    def reset_game(self):
        self.game.reset()
        self.winning_pieces = []
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    gui = Connect4GUI(root)
    root.mainloop()