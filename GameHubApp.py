import tkinter as tk
from tkinter import messagebox

# Import the GUI classes
try:
    from Connect4_game.connect4_gui import connect4Gui
except ImportError:
    connect4Gui = None

try:
    from Sudoku_game.sudoku_gui import SudokuGUI
except ImportError:
    SudokuGUI = None

try:
    from eight_puzzle_gui import EightPuzzleGUI
except ImportError:
    EightPuzzleGUI = None

class GameHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GameHub")
        # Set Full Screen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#1a1a2e")
        
        # This variable tracks the currently active frame (Menu or Game)
        self.current_frame = None

        # Start by showing the menu
        self.show_menu()

    def show_menu(self):
        """Clears whatever is on screen and shows the GameHub Menu"""
        if self.current_frame:
            self.current_frame.destroy()

        # Create a container for the menu
        self.current_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.current_frame.pack(fill="both", expand=True)

        # --- Header ---
        title_label = tk.Label(
            self.current_frame, 
            text="GameHub", 
            font=("Helvetica", 40, "bold"), # Larger for fullscreen
            bg="#1a1a2e",
            fg="#e94560"
        )
        title_label.pack(pady=(80, 10))

        subtitle_label = tk.Label(
            self.current_frame, 
            text="Instructor: Mohamed Maher Ben Ismail", 
            font=("Helvetica", 14, "italic"),
            bg="#1a1a2e",
            fg="#fcdab7" 
        )
        subtitle_label.pack(pady=(0, 50))

        # --- Buttons ---
        self.create_button("Sudoku", self.launch_sudoku)
        self.create_button("Connect 4", self.launch_connect4)
        self.create_button("8-Puzzle", self.launch_eight_puzzle)
        self.create_button("Credits", self.show_credits)
        
        # Exit Button
        exit_btn = tk.Button(
            self.current_frame,
            text="Exit",
            font=("Arial", 16, "bold"),
            bg="#e94560",
            fg="black",
            width=20,
            activebackground="#c73e52",
            activeforeground="#ffffff",
            bd=0,
            command=self.exit_app
        )
        exit_btn.pack(pady=30)

    def create_button(self, text, command):
        btn = tk.Button(
            self.current_frame,
            text=text,
            font=("Arial", 16),
            bg="#16213e",
            fg="black",
            width=20,
            activebackground="#0f3460",
            activeforeground="#ffffff",
            bd=0, 
            command=command
        )
        btn.pack(pady=10)

    # --- Launchers ---

    def launch_sudoku(self):
        if SudokuGUI:
            # Destroy Menu
            if self.current_frame:
                self.current_frame.destroy()
            
            # Initialize Sudoku
            self.app = SudokuGUI(self.root, on_back=self.show_menu)
            
            # Sudoku manages its own frames
            self.current_frame = None
        else:
            messagebox.showerror("Error", "sudoku_gui.py not found.")

    def launch_connect4(self):
        if connect4Gui:
            # Destroy Menu
            if self.current_frame:
                self.current_frame.destroy()
            
            # Initialize Connect4
            # We pass 'self.show_menu' as the callback for the Back button
            self.app = connect4Gui(self.root, on_back=self.show_menu)
            
            # Connect4 manages its own frames on root
            self.current_frame = None
        else:
            messagebox.showerror("Error", "connect4_gui.py not found.")

    def launch_eight_puzzle(self):
        if EightPuzzleGUI:
            # Destroy Menu
            if self.current_frame:
                self.current_frame.destroy()
            
            # Initialize 8-Puzzle
            self.app = EightPuzzleGUI(self.root, on_back=self.show_menu)
            
            # 8-Puzzle manages its own frames
            self.current_frame = None
        else:
            messagebox.showerror("Error", "eight_puzzle_gui.py not found.")

    def launch_chess(self):
        messagebox.showinfo("Chess", "Chess module not yet implemented.")

    def show_credits(self):
        messagebox.showinfo("Credits", "Build By:\nMohammed\nAlwaleed\nMajed")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameHubApp(root)
    root.mainloop()