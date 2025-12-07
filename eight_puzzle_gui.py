import tkinter as tk
from tkinter import messagebox
import time
import math

class Node:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority
        self.next = None

class PriorityQueue:
    def __init__(self):
        self.head = None

    def enqueue(self, data, priority):
        newNode = Node(data, priority)
        if self.head is None or priority < self.head.priority:
            newNode.next = self.head
            self.head = newNode
        else:
            current = self.head
            while current.next is not None and current.next.priority <= priority:
                current = current.next
            newNode.next = current.next
            current.next = newNode

    def dequeue(self):
        if self.isEmpty():
            raise Exception("Priority Queue is empty")
        result = self.head.data
        self.head = self.head.next
        return result

    def peek(self):
        if self.isEmpty():
            raise Exception("Priority Queue is empty")
        return self.head.data

    def isEmpty(self):
        return self.head is None

    def inFrontier(self, c):
        tmp = self.head
        while tmp is not None:
            if tmp == c:
                return True
            tmp = tmp.next
        return False

class Board:
    depth = 0 

    def __init__(self, arg1=None, arg2=None, arg3=None):
        self.rows = [[0 for _ in range(3)] for _ in range(3)]
        self.parent = None
        self.depthObject = 0

        if isinstance(arg1, str):
            num = arg1
            idxPointer = 0
            for i in range(3):
                for j in range(3):
                    c = num[idxPointer] + ""
                    idxPointer += 1
                    self.rows[i][j] = int(c)
            self.parent = None
            Board.depth = 0
            self.depthObject = 0

        elif isinstance(arg1, list) and isinstance(arg2, list) and isinstance(arg3, list):
            self.rows[0] = arg1
            self.rows[1] = arg2
            self.rows[2] = arg3
            self.parent = None
            Board.depth = 0
            self.depthObject = 0

        else:
            r1 = [0] * 3
            r2 = [0] * 3
            r3 = [0] * 3
            self.rows[0] = r1
            self.rows[1] = r2
            self.rows[2] = r3
            self.parent = None
            Board.depth = 0
            self.depthObject = 0

    def blankPos(self):
        res = [0] * 2
        for i in range(3):
            for j in range(3):
                if self.rows[i][j] == 0:
                    res[0] = i
                    res[1] = j
                    return res
        return None

    def Pos(self, n):
        res = [0] * 2
        for i in range(3):
            for j in range(3):
                if self.rows[i][j] == n:
                    res[0] = i
                    res[1] = j
                    return res
        return None

    def adjElements(self):
        adj = []
        corner = 0
        mid = 0
        other = 0
        possibleAdj = 0
        Blank = self.blankPos()

        if (Blank[0] == 0 or Blank[0] == 2) and (Blank[1] == 0 or Blank[1] == 2):
            corner = 1
            possibleAdj = 2
        elif Blank[0] == 1 and Blank[1] == 1:
            mid = 1
            possibleAdj = 4
        else:
            other = 1
            possibleAdj = 3

        adj = [0] * possibleAdj

        if corner == 1:
            if Blank[0] == 0:
                adj[0] = self.rows[1][Blank[1]]
                adj[1] = self.rows[0][1]
            else:
                adj[0] = self.rows[1][Blank[1]]
                adj[1] = self.rows[2][1]
        elif mid == 1:
            adj[0] = self.rows[0][1]
            adj[1] = self.rows[1][0]
            adj[2] = self.rows[2][1]
            adj[3] = self.rows[1][2]
        else:
            if Blank[0] == 0 or Blank[0] == 2:
                adj[0] = self.rows[Blank[0]][0]
                adj[1] = self.rows[1][1] 
                adj[2] = self.rows[Blank[0]][2]
            else:
                adj[0] = self.rows[0][Blank[1]]
                adj[1] = self.rows[1][1] 
                adj[2] = self.rows[2][Blank[1]]
        return adj

    def calcHurstic(self):
        sum_val = 0
        for i in range(3):
            for j in range(3):
                val = self.rows[i][j]
                if val == 0: continue
                target_r = (val - 1) // 3
                target_c = (val - 1) % 3
                sum_val += abs(i - target_r) + abs(j - target_c)
        return sum_val

    def change(self, i, j, element):
        self.rows[i][j] = element

    def changeAsCopy(self, element):
        b = Board()
        for i in range(3):
            for j in range(3):
                b.change(i, j, self.rows[i][j])

        posZero = self.blankPos()
        posTarget = self.Pos(element)
        b.change(posZero[0], posZero[1], element)
        b.change(posTarget[0], posTarget[1], 0)
        b.depthObject = self.depthObject
        return b

    def Sucssours(self, blist, size, frointer, algorithm):
        adj = self.adjElements()
        suc = [None] * len(adj)
        for i in range(len(adj)):
            tmp = self.changeAsCopy(adj[i])
            tmp.parent = self
            if self.parent is not None:
                tmp.depthObject = self.parent.depthObject + 1
            suc[i] = tmp

        for i in range(len(suc)):
            if not frointer.inFrontier(suc[i]) and not Board.dublicate(suc[i], blist, size):
                if algorithm.lower() == "a*":
                    frointer.enqueue(suc[i], suc[i].calcHurstic() + suc[i].depthObject)
                elif algorithm.lower() == "greedy":
                    frointer.enqueue(suc[i], suc[i].calcHurstic())

    def getBoardString(self):
        res = ""
        for i in range(3):
            for j in range(3):
                res += str(self.rows[i][j])
        return res

    @staticmethod
    def equal(b1, b2):
        rows2 = b2.rows
        rows1 = b1.rows
        for i in range(3):
            for j in range(3):
                if rows1[i][j] != rows2[i][j]:
                    return False
        return True

    @staticmethod
    def dublicate(b, bList, size):
        for i in range(size):
            if Board.equal(b, bList[i]):
                return True
        return False

class Solver:
    def __init__(self):
        self.steps = 0
        self.timeTaken = 0
        self.solution = []

    def SolveByGreedy(self, num):
        startTime = time.time_ns()
        frontier = PriorityQueue()
        b = Board(num)
        bList = [None] * 3000 # Increased buffer slightly
        counter = 0
        idx = 0
        
        # Check initial state
        if b.calcHurstic() == 0:
             self.solution = [b]
             self.steps = 0
             self.timeTaken = 0
             return

        while b.calcHurstic() != 0:
            if idx >= 2999: break # Safety break
            bList[idx] = b
            idx += 1
            counter += 1
            b.Sucssours(bList, counter, frontier, "Greedy")
            if frontier.isEmpty(): break
            b = frontier.dequeue()

        sum_val = 0
        idx_sol = 0
        temp_sol = []
        
        curr = b
        while curr is not None:
            temp_sol.append(curr)
            curr = curr.parent
        
        # Reverse to get start -> goal
        self.solution = temp_sol[::-1]
        self.steps = len(self.solution) - 1
        endTime = time.time_ns()
        self.timeTaken = endTime - startTime

    def SolveByAstar(self, num):
        startTime = time.time_ns()
        frontier = PriorityQueue()
        b = Board(num)
        bList = [None] * 3000
        counter = 0
        idx = 0
        
        if b.calcHurstic() == 0:
             self.solution = [b]
             self.steps = 0
             self.timeTaken = 0
             return

        while b.calcHurstic() != 0:
            if idx >= 2999: break
            bList[idx] = b
            idx += 1
            counter += 1
            b.Sucssours(bList, counter, frontier, "A*")
            if frontier.isEmpty(): break
            b = frontier.dequeue()

        temp_sol = []
        curr = b
        while curr is not None:
            temp_sol.append(curr)
            curr = curr.parent

        self.solution = temp_sol[::-1]
        self.steps = len(self.solution) - 1
        endTime = time.time_ns()
        self.timeTaken = endTime - startTime


def solve_logic_A(start_state):
    """ Returns: (path_list, time_taken, total_steps) """
    s=Solver()
    s.SolveByGreedy(start_state)
    solutionss=s.solution
    path = []
    for b in solutionss:
        path.append(b.getBoardString())
    
    # Handle case where solution is empty or failed
    if not path: path = [start_state]

    return path, (str(s.timeTaken*10**-9)[:6]), s.steps

def solve_logic_B(start_state):
    """ Returns: (path_list, time_taken, total_steps) """
    s=Solver()
    s.SolveByAstar(start_state)
    solutionss=s.solution
    path = []
    for b in solutionss:
        path.append(b.getBoardString())

    if not path: path = [start_state]

    return path, (str(s.timeTaken*10**-9)[:6]), s.steps
    

class EightPuzzleGUI:
    def __init__(self, root, on_back=None):
        self.root = root
        self.on_back = on_back
        self.root.title("8-Puzzle Dual Solver")
        
        self.BG_COLOR = "#1a1a2e"       
        self.FG_COLOR = "#ffffff"       
        self.ACCENT_COLOR = "#e94560"   
        self.BTN_BG = "#16213e"         
        self.BTN_ACTIVE = "#0f3460"     
        self.CARD_BG = "#16213e"        
        self.TILE_BG = "#e94560"        
        self.TILE_FG = "#ffffff"        
        self.INPUT_BG = "#0f3460"       

        self.main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.main_frame.pack(fill="both", expand=True)

        self.data_A = {"path": [], "idx": 0}
        self.data_B = {"path": [], "idx": 0}
        
        self.setup_ui()

    def setup_ui(self):
        self.input_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        self.input_frame.pack(fill="both", expand=True, pady=100)

        tk.Label(self.input_frame, 
                 text="Compare Two Algorithms", 
                 font=("Helvetica", 30, "bold"), 
                 bg=self.BG_COLOR, 
                 fg=self.ACCENT_COLOR).pack(pady=(0, 30))
        
        self.input_entry = tk.Entry(self.input_frame, 
                                    font=("Arial", 22), 
                                    width=15, 
                                    justify="center", 
                                    bd=0, 
                                    bg=self.INPUT_BG,
                                    fg="white",
                                    insertbackground="white") # Cursor color
        self.input_entry.pack(pady=20, ipady=5)
        self.input_entry.bind('<Return>', self.start_solver)
        
        self.create_styled_button(self.input_frame, "COMPARE", self.start_solver, bg_override="#e94560", fg_override="black").pack(pady=10)

        if self.on_back:
             self.create_styled_button(self.input_frame, "BACK", self.go_back).pack(pady=10)

        self.solver_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        
        self.frame_A = tk.Frame(self.solver_frame, bg=self.BG_COLOR)
        self.frame_A.pack(side="left", fill="both", expand=True, padx=20)


        self.frame_B = tk.Frame(self.solver_frame, bg=self.BG_COLOR)
        self.frame_B.pack(side="right", fill="both", expand=True, padx=20)


        tk.Frame(self.solver_frame, bg=self.BTN_BG, width=2).place(relx=0.5, rely=0.1, relheight=0.8)
        

        self.lbl_time_A, self.lbl_steps_A, self.lbl_prog_A, self.grid_labels_A = self.create_solver_panel(
            self.frame_A, "Greedy Algorithm", self.prev_A, self.next_A
        )
        
        self.lbl_time_B, self.lbl_steps_B, self.lbl_prog_B, self.grid_labels_B = self.create_solver_panel(
            self.frame_B, "A* Algorithm", self.prev_B, self.next_B
        )
        
        if self.on_back:
             self.create_styled_button(self.solver_frame, "BACK", self.go_back).pack(side="bottom", pady=30)


    def create_styled_button(self, parent, text, command, bg_override=None, fg_override=None):
        bg = bg_override if bg_override else self.BTN_BG
        # GameHub uses black text on buttons often, but can use white if preferred. 
        # Using white for non-accent buttons looks cleaner on dark theme, but following request:
        fg = fg_override if fg_override else "white" 
        
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 14, "bold"),
            bg=bg,
            fg=fg,
            width=20,
            activebackground=self.BTN_ACTIVE,
            activeforeground="white",
            bd=0, 
            command=command
        )
        return btn

    def create_solver_panel(self, parent, title, prev_cmd, next_cmd):
        tk.Label(parent, text=title, font=("Helvetica", 20, "bold"), bg=self.BG_COLOR, fg=self.ACCENT_COLOR).pack(pady=(40, 15))

        stats = tk.Frame(parent, bg=self.CARD_BG, padx=15, pady=10)
        stats.pack(fill="x", padx=40)

        r1 = tk.Frame(stats, bg=self.CARD_BG)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Time:", font=("Arial", 11, "bold"), bg=self.CARD_BG, fg="#ccc").pack(side="left")
        t_lbl = tk.Label(r1, text="0s", font=("Arial", 11, "bold"), bg=self.CARD_BG, fg="#4CAF50") # Green for success metrics
        t_lbl.pack(side="right")

        r2 = tk.Frame(stats, bg=self.CARD_BG)
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Steps:", font=("Arial", 11, "bold"), bg=self.CARD_BG, fg="#ccc").pack(side="left")
        s_lbl = tk.Label(r2, text="0", font=("Arial", 11, "bold"), bg=self.CARD_BG, fg="#4CAF50")
        s_lbl.pack(side="right")

        p_lbl = tk.Label(parent, text="Step: 0", font=("Arial", 12), bg=self.BG_COLOR, fg=self.FG_COLOR)
        p_lbl.pack(pady=(20, 10))

        g_cont = tk.Frame(parent, bg=self.BG_COLOR)
        g_cont.pack(pady=10)
        labels = []
        for r in range(3):
            for c in range(3):
                # Placeholder style
                l = tk.Label(g_cont, 
                             text="?", 
                             font=("Helvetica", 24, "bold"), 
                             width=4, 
                             height=2, 
                             bg=self.BTN_BG, 
                             fg=self.FG_COLOR,
                             relief="flat")
                l.grid(row=r, column=c, padx=4, pady=4)
                labels.append(l)

        nav = tk.Frame(parent, bg=self.BG_COLOR)
        nav.pack(pady=20)
        
        btn_prev = tk.Button(nav, text="◄", command=prev_cmd, font=("Arial", 14), bg=self.BTN_BG, fg="white", bd=0, activebackground=self.BTN_ACTIVE, activeforeground="white", width=5)
        btn_prev.pack(side="left", padx=10)
        
        btn_next = tk.Button(nav, text="►", command=next_cmd, font=("Arial", 14), bg=self.BTN_BG, fg="white", bd=0, activebackground=self.BTN_ACTIVE, activeforeground="white", width=5)
        btn_next.pack(side="left", padx=10)

        return t_lbl, s_lbl, p_lbl, labels

    def start_solver(self, event=None):
        raw_input = self.input_entry.get()
        clean_input = "".join([char for char in raw_input if char.isdigit()])

        if len(clean_input) != 9:
            messagebox.showerror("Error", "Please enter exactly 9 digits.")
            return

        path_a, time_a, steps_a = solve_logic_A(clean_input)
        self.data_A["path"] = path_a
        self.data_A["idx"] = 0

        self.lbl_time_A.config(text=f"{time_a}s")
        self.lbl_steps_A.config(text=str(steps_a))
        self.draw_grid(self.grid_labels_A, path_a[0])
        self.update_label_A()


        path_b, time_b, steps_b = solve_logic_B(clean_input)
        self.data_B["path"] = path_b
        self.data_B["idx"] = 0


        self.lbl_time_B.config(text=f"{time_b}s")
        self.lbl_steps_B.config(text=str(steps_b))
        self.draw_grid(self.grid_labels_B, path_b[0])
        self.update_label_B()


        self.input_frame.pack_forget()
        self.solver_frame.pack(fill="both", expand=True)

    def draw_grid(self, label_list, state_string):
        for i, char in enumerate(state_string):
            lbl = label_list[i]
            if char == '0':
                lbl.config(text="", bg=self.BTN_BG) 
            else:
                lbl.config(text=char, bg=self.ACCENT_COLOR, fg="white")

    def prev_A(self):
        if self.data_A["idx"] > 0:
            self.data_A["idx"] -= 1
            self.draw_grid(self.grid_labels_A, self.data_A["path"][self.data_A["idx"]])
            self.update_label_A()

    def next_A(self):
        if self.data_A["idx"] < len(self.data_A["path"]) - 1:
            self.data_A["idx"] += 1
            self.draw_grid(self.grid_labels_A, self.data_A["path"][self.data_A["idx"]])
            self.update_label_A()

    def update_label_A(self):
        self.lbl_prog_A.config(text=f"Step: {self.data_A['idx']} / {len(self.data_A['path']) - 1}")

    def prev_B(self):
        if self.data_B["idx"] > 0:
            self.data_B["idx"] -= 1
            self.draw_grid(self.grid_labels_B, self.data_B["path"][self.data_B["idx"]])
            self.update_label_B()

    def next_B(self):
        if self.data_B["idx"] < len(self.data_B["path"]) - 1:
            self.data_B["idx"] += 1
            self.draw_grid(self.grid_labels_B, self.data_B["path"][self.data_B["idx"]])
            self.update_label_B()

    def update_label_B(self):
        self.lbl_prog_B.config(text=f"Step: {self.data_B['idx']} / {len(self.data_B['path']) - 1}")
        
    def go_back(self):
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()
        if self.on_back:
            self.on_back()

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#1a1a2e")
    app = EightPuzzleGUI(root)
    root.mainloop()
