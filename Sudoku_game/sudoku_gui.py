import tkinter as tk
from tkinter import ttk, messagebox, font
import time
import threading 
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sudoku_game import SudokuGame

class SudokuGUI:
    def __init__(self, root, on_back=None):
        self.root = root
        self.on_back = on_back
        self.root.title("Sudoku AI Project - Final Submission")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        self.root.configure(bg="#1a1a2e")
        
        self.game = SudokuGame()
        self.cells = {} 
        self.generated_cells = set() 
        
        self.default_font = font.Font(family="Helvetica", size=12)
        self.cell_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.btn_font = font.Font(family="Helvetica", size=11, weight="bold")
        
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = tk.Label(self.main_frame, text="Sudoku Solver", bg="#1a1a2e", fg="#e94560", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=(0, 10))

        control_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Dark.TCombobox",
            fieldbackground="#0f3460", 
            background="#0f3460",   
            foreground="white",
            bordercolor="#FFFFFF",
            lightcolor="#102036",
            darkcolor="#102036"
        )
        
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", "#102036")],
            background=[("active", "#203354")],
            foreground=[("readonly", "white")]
        )

        top_controls = tk.Frame(control_frame, bg="#1a1a2e")
        top_controls.pack(fill=tk.X, pady=(0, 5))

        tk.Label(top_controls, text="Difficulty:", bg="#1a1a2e",fg="#fcdab7" ,font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        self.diff_var = tk.StringVar(value="Extreme")
        ttk.Combobox(top_controls,
                     textvariable=self.diff_var,
                     values=["Easy", "Medium", "Hard", "Expert", "Extreme"],
                     state="readonly",
                     width=10,
                     font=("Helvetica", 11),
                     style="Dark.TCombobox"
                     ).pack(side=tk.LEFT, padx=10)

        algo_frame = tk.Frame(control_frame, bg="#1a1a2e")
        algo_frame.pack(fill=tk.X, pady=(0, 10))

        
        
        tk.Label(algo_frame, text="Algorithm:", bg="#1a1a2e",fg="#fcdab7", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        self.algo_var = tk.StringVar(value="Smart CSP (MRV)")
        algo_combo = ttk.Combobox(
            algo_frame, 
            textvariable=self.algo_var, 
            values=["Smart CSP (MRV)", "Naive Backtracking", "Simulated Annealing (Numpy)"], 
            state="readonly", 
            width=25,
            font=("Helvetica", 11),
            style="Dark.TCombobox" 
        )
        algo_combo.pack(side=tk.LEFT, padx=10)

        self.time_label = tk.Label(algo_frame, text="0.00s", font=("Courier", 16, "bold"), bg="#1a1a2e", fg="#ffffff")
        self.time_label.pack(side=tk.RIGHT)

        stats_frame = tk.Frame(control_frame, bg="#1a1a2e", pady=5)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        self.stats_label = tk.Label(stats_frame, text="Steps: 0  |  Backtracks: 0", font=("Courier", 14), bg="#1D1D49", fg="#FFFFFF")
        self.stats_label.pack()

        btn_frame = tk.Frame(control_frame, bg="#1a1a2e")
        btn_frame.pack(fill=tk.X)

        self.btn_gen = tk.Button(btn_frame, text="Generate", command=self.generate_new, bg="#2196F3", fg="black", font=self.btn_font, relief="flat", padx=10, pady=5)
        self.btn_gen.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_solve = tk.Button(btn_frame, text="Start Solving", command=self.solve_puzzle, bg="#4CAF50", fg="black", font=self.btn_font, relief="flat", padx=5, pady=5)
        self.btn_solve.pack(side=tk.LEFT, padx=5)

        if self.on_back:
            self.btn_back = tk.Button(btn_frame, text="Back", command=self.go_back, bg="#922b21", fg="black", font=self.btn_font, relief="flat", padx=10, pady=5)
            self.btn_back.pack(side=tk.RIGHT, padx=5)

        

        self.btn_clear = tk.Button(btn_frame, text="Reset", command=self.reset_board, bg="#FF9800", fg="black", font=self.btn_font, relief="flat", padx=10, pady=5)
        self.btn_clear.pack(side=tk.RIGHT, padx=5)

        self.grid_wrapper = tk.Frame(self.main_frame, bg="#444", padx=4, pady=4)
        self.grid_wrapper.pack()
        self.grid_frame = tk.Frame(self.grid_wrapper, bg="#444")
        self.grid_frame.pack()

        for r in range(9):
            for c in range(9):
                pad_top = 6 if r % 3 == 0 and r != 0 else 1
                pad_left = 6 if c % 3 == 0 and c != 0 else 1
                cell = tk.Entry(self.grid_frame, width=2, font=self.cell_font, justify="center", bd=0)
                cell.grid(row=r, column=c, padx=(pad_left, 1), pady=(pad_top, 1), ipady=5)
                self.cells[(r, c)] = cell

        self.status_label = tk.Label(self.root, text="Ready.", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#e0e0e0", padx=10, pady=5)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def update_gui_from_board(self):
        for r in range(9):
            for c in range(9):
                val = self.game.board[r][c]
                cell = self.cells[(r, c)]
                cell.delete(0, tk.END)
                if val != 0: cell.insert(0, str(val))
                if (r, c) in self.generated_cells:
                    cell.config(fg="#000", bg="#e0e0e0", state="disabled", disabledbackground="#e0e0e0", disabledforeground="#000")
                else:
                    cell.config(state="normal", bg="#fff", fg="#000")

    def reset_board(self):
        if not self.game.original_board: return
        self.game.board = [row[:] for row in self.game.original_board]
        self.update_gui_from_board()
        self.status_label.config(text="Board reset.")
        self.time_label.config(text="0.00s")
        self.stats_label.config(text="Steps: 0  |  Backtracks: 0")

    def generate_new(self):
        diff_map = {"Easy": 0.4, "Medium": 0.5, "Hard": 0.65, "Expert": 0.75, "Extreme": 0.85}
        difficulty = diff_map.get(self.diff_var.get(), 0.5)

        try:
            self.status_label.config(text="Generating...")
            self.root.update()
            
            self.game.generate_puzzle(difficulty)
            
            self.generated_cells.clear()
            for r in range(9):
                for c in range(9):
                    if self.game.board[r][c] != 0: self.generated_cells.add((r, c))
            
            self.update_gui_from_board()
            self.time_label.config(text="0.00s")
            self.stats_label.config(text="Steps: 0  |  Backtracks: 0")
            self.status_label.config(text=f"Generated ({self.diff_var.get()})")

        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def solve_puzzle(self):
        for r in range(9):
            for c in range(9):
                if (r, c) in self.generated_cells: continue
                val = self.cells[(r, c)].get()
                if val.isdigit() and int(val) in range(1, 10):
                    self.game.board[r][c] = int(val)
                else:
                    self.game.board[r][c] = 0

        algo_choice = self.algo_var.get()
        self.status_label.config(text=f"Solving using {algo_choice}...")
        self.root.update()

        start_time = time.perf_counter()
        
        if "Smart" in algo_choice:
            solver = self.game.solve_csp_generator() 
        elif "Naive" in algo_choice:
            solver = self.game.solve_naive_generator()
        else:
            solver = self.game.solve_annealing_generator()

        solved = False
        step_counter = 0 
        
        try:
            while True:
                step = next(solver)
                row, col, val, metric1, metric2 = step
                
                step_counter += 1
                
                if "Annealing" in algo_choice:
                    self.stats_label.config(text=f"Iteration: {metric1}  |  Cost/Errors: {metric2}")
                    if row != -1: # -1 indicates just a cost update
                        cell = self.cells[(row, col)]
                        cell.delete(0, tk.END)
                        cell.insert(0, str(val))
                        cell.config(bg="#E1BEE7")
                else:
                    self.stats_label.config(text=f"Steps: {metric1}  |  Backtracks: {metric2}")
                    cell = self.cells[(row, col)]
                    cell.delete(0, tk.END)
                    if val != 0:
                        cell.insert(0, str(val))
                        cell.config(bg="#FFF176") 
                    else:
                        cell.config(bg="#FFCDD2") 

                if "Naive" in algo_choice and step_counter % 5 != 0: pass
                elif "Annealing" in algo_choice and step_counter % 20 != 0: pass
                else: self.root.update_idletasks()

        except StopIteration as e:
            solved = e.value

        end_time = time.perf_counter()
        duration = end_time - start_time

        if solved or "Annealing" in algo_choice:
            if "Annealing" not in algo_choice:
                for r in range(9):
                    for c in range(9):
                        if (r, c) not in self.generated_cells:
                            self.cells[(r, c)].config(bg="#C8E6C9", fg="#2E7D32") 
            else: 
                self.update_gui_from_board()
                for r in range(9):
                    for c in range(9):
                         if (r, c) not in self.generated_cells:
                            self.cells[(r, c)].config(bg="#C8E6C9", fg="#2E7D32") 

            self.time_label.config(text=f"{duration:.2f}s")
            self.status_label.config(text=f"Finished in {duration:.4f}s")
        else:
            self.status_label.config(text="No solution found / Stuck.")
            messagebox.showwarning("Result", "Solver stopped or could not find solution.")

    
    def open_analysis_window(self):
        win = tk.Toplevel(self.root)
        win.title("Algorithm Performance Analysis")
        win.geometry("400x400")
        
        tk.Label(win, text="Batch Analysis Tool", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        results_text = tk.Text(win, height=15, width=45)
        results_text.pack(pady=10)
        
        def run_tests():
            results_text.insert(tk.END, "Running Smart CSP...\n")
            win.update()
            res_csp = self.game.run_batch_analysis("Smart CSP", 5)
            results_text.insert(tk.END, f"CSP: {res_csp['avg_time']}\n\n")
            
            results_text.insert(tk.END, "Running Annealing...\n")
            win.update()
            res_sa = self.game.run_batch_analysis("Annealing", 1) 
            results_text.insert(tk.END, f"Annealing: {res_sa['avg_time']}\n\n")
            
            results_text.insert(tk.END, "DONE.")
            
        btn = tk.Button(win, text="Start Test", command=run_tests, bg="#2196F3", fg="white")
        btn.pack(pady=5)

    def go_back(self):
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()
        if self.on_back:
            self.on_back()

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
