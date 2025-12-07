import tkinter as tk
from tkinter import messagebox
import time

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

    def printQueue(self):
        current = self.head
        while current is not None:
            print("(" + str(current.data) + ", priority: " + str(current.priority) + ") -> ", end="")
            current = current.next
        print("null")

    def inFrontier(self, c):
        tmp = self.head
        while tmp is not None:
            if tmp == c:
                return True
            tmp = tmp.next
        return False


class Board:
    depth = 0  # static variable

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

    def print(self):
        for j in range(3):
            for i in range(3):
                print(str(self.rows[j][i]) + " ", end="")
            print()
        print("-----")

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
                adj[1] = self.rows[1][1]  # mid
                adj[2] = self.rows[Blank[0]][2]
            else:
                adj[0] = self.rows[0][Blank[1]]
                adj[1] = self.rows[1][1]  # mid
                adj[2] = self.rows[2][Blank[1]]

        return adj

    def calcHurstic(self):
        sum_val = 0

        for i in range(3):
            for j in range(3):
                if self.rows[i][j] == 1:
                    sum_val += abs(i - 0) + abs(j - 0)
                elif self.rows[i][j] == 2:
                    sum_val += abs(i - 0) + abs(j - 1)
                elif self.rows[i][j] == 3:
                    sum_val += abs(i - 0) + abs(j - 2)
                elif self.rows[i][j] == 4:
                    sum_val += abs(i - 1) + abs(j - 0)
                elif self.rows[i][j] == 5:
                    sum_val += abs(i - 1) + abs(j - 1)
                elif self.rows[i][j] == 6:
                    sum_val += abs(i - 1) + abs(j - 2)
                elif self.rows[i][j] == 7:
                    sum_val += abs(i - 2) + abs(j - 0)
                elif self.rows[i][j] == 8:
                    sum_val += abs(i - 2) + abs(j - 1)
                else:
                    continue
        return sum_val

    def change(self, i, j, element):
        self.rows[i][j] = element

    def Copy(self, element):
        b = Board()
        for i in range(3):
            for j in range(3):
                b.change(i, j, self.rows[i][j])
        return b

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

    def Sucssours(self, blist, size, frointer, algorithm):  #
        adj = self.adjElements()

        bl = []  # ArrayList<Board>

        suc = [None] * len(adj)
        idx = 0
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
        explore = []  # ArrayList<Board>
        frontier = PriorityQueue()
        b = Board(num)

        bList = [None] * 1000
        counter = 0
        idx = 0
        while b.calcHurstic() != 0:
            bList[idx] = b
            idx += 1
            counter += 1
            b.Sucssours(bList, counter, frontier, "Greedy")
            b = frontier.dequeue()

        sum_val = 0
        # b.print();
        idx = 999
        sol = [None] * 1000

        while b.parent is not None:
            sol[idx] = b
            idx -= 1
            b = b.parent

        sol[idx] = b

        finalSol = [None] * (1000 - idx)
        c = 0
        for i in range(idx, 1000):
            finalSol[c] = sol[i]
            c += 1
            sum_val += 1

        self.solution = finalSol
        self.steps = sum_val - 1
        endTime = time.time_ns()
        self.timeTaken = endTime - startTime

    def SolveByAstar(self, num):
        startTime = time.time_ns()
        explore = []  # ArrayList<Board>
        frontier = PriorityQueue()
        b = Board(num)

        bList = [None] * 1000
        counter = 0
        idx = 0
        while b.calcHurstic() != 0:
            bList[idx] = b
            idx += 1
            counter += 1
            b.Sucssours(bList, counter, frontier, "A*")
            b = frontier.dequeue()

        sum_val = 0
        idx = 999
        sol = [None] * 1000

        while b.parent is not None:
            sol[idx] = b
            idx -= 1
            b = b.parent

        sol[idx] = b

        finalSol = [None] * (1000 - idx)
        c = 0
        for i in range(idx, 1000):
            finalSol[c] = sol[i]
            c += 1
            sum_val += 1

        self.solution = finalSol
        self.steps = sum_val - 1
        endTime = time.time_ns()
        self.timeTaken = endTime - startTime

    def print(self):
        for i in range(len(self.solution)):
            self.solution[i].print()



def solve_logic_A(start_state):
    s=Solver()
    s.SolveByGreedy(start_state)
    solutionss=s.solution
    path = [start_state]
    t=1
    for i in solutionss:
        if(t==1):
            t=t+1
            temp = list(start_state)
            path.append("".join(temp))
            continue
        b = i
        result_string = b.getBoardString()
        path.append(result_string)

    return path, (str(s.timeTaken*10**-9)[:5]), s.steps



def solve_logic_B(start_state):

    s=Solver()
    s.SolveByAstar(start_state)
    solutionss=s.solution
    t=1
    for i in solutionss:
        if(t==1):
            path = [start_state]
            t=t+1
            temp = list(start_state)
            path.append("".join(temp))
            continue
        b = i
        result_string = b.getBoardString()
        path.append(result_string)

    return path, (str(s.timeTaken*10**-9)[:5]), s.steps



data_A = {"path": [], "idx": 0}
data_B = {"path": [], "idx": 0}


def start_solver(event=None):
    raw_input = input_entry.get()
    clean_input = "".join([char for char in raw_input if char.isdigit()])

    if len(clean_input) != 9:
        messagebox.showerror("Error", "Please enter exactly 9 digits.")
        return

    path_a, time_a, steps_a = solve_logic_A(clean_input)
    data_A["path"] = path_a
    data_A["idx"] = 0

    lbl_time_A.config(text=f"{time_a}s")
    lbl_steps_A.config(text=str(steps_a))
    draw_grid(grid_labels_A, path_a[0])
    update_label_A()

    path_b, time_b, steps_b = solve_logic_B(clean_input)
    data_B["path"] = path_b
    data_B["idx"] = 0

    lbl_time_B.config(text=f"{time_b}s")
    lbl_steps_B.config(text=str(steps_b))
    draw_grid(grid_labels_B, path_b[0])
    update_label_B()

    input_frame.pack_forget()
    solver_frame.pack(fill="both", expand=True)


def draw_grid(label_list, state_string):
    for i, char in enumerate(state_string):
        lbl = label_list[i]
        if char == '0':
            lbl.config(text="", bg="#f0f0f0")
        else:
            lbl.config(text=char, bg="#2196F3", fg="white")


def prev_A():
    if data_A["idx"] > 0:
        data_A["idx"] -= 1
        draw_grid(grid_labels_A, data_A["path"][data_A["idx"]])
        update_label_A()


def next_A():
    if data_A["idx"] < len(data_A["path"]) - 1:
        data_A["idx"] += 1
        draw_grid(grid_labels_A, data_A["path"][data_A["idx"]])
        update_label_A()


def update_label_A():
    lbl_prog_A.config(text=f"Step: {data_A['idx']} / {len(data_A['path']) - 1}")


def prev_B():
    if data_B["idx"] > 0:
        data_B["idx"] -= 1
        draw_grid(grid_labels_B, data_B["path"][data_B["idx"]])
        update_label_B()


def next_B():
    if data_B["idx"] < len(data_B["path"]) - 1:
        data_B["idx"] += 1
        draw_grid(grid_labels_B, data_B["path"][data_B["idx"]])
        update_label_B()


def update_label_B():
    lbl_prog_B.config(text=f"Step: {data_B['idx']} / {len(data_B['path']) - 1}")



root = tk.Tk()
root.title("8-Puzzle Dual Solver")
root.geometry("900x650")  
root.configure(bg="white")


input_frame = tk.Frame(root, bg="white")
input_frame.pack(fill="both", expand=True, pady=100)

tk.Label(input_frame, text="Compare Two Algorithms", font=("Helvetica", 24, "bold"), bg="white", fg="#333").pack(
    pady=(0, 20))
input_entry = tk.Entry(input_frame, font=("Arial", 18), width=15, justify="center", bd=2, relief="groove")
input_entry.pack(pady=15)
input_entry.bind('<Return>', start_solver)
tk.Button(input_frame, text="COMPARE", command=start_solver, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"),
          padx=20, pady=5).pack(pady=10)


solver_frame = tk.Frame(root, bg="white")


frame_A = tk.Frame(solver_frame, bg="white", width=450)
frame_A.pack(side="left", fill="both", expand=True, padx=10)


frame_B = tk.Frame(solver_frame, bg="white", width=450)
frame_B.pack(side="right", fill="both", expand=True, padx=10)


tk.Frame(solver_frame, bg="#ccc", width=2).place(relx=0.5, rely=0.1, relheight=0.8)



def create_solver_panel(parent, title, time_lbl_var, steps_lbl_var, prog_lbl_var, prev_cmd, next_cmd):
    tk.Label(parent, text=title, font=("Helvetica", 18, "bold"), bg="white", fg="#333").pack(pady=(20, 10))


    stats = tk.Frame(parent, bg="#f9f9f9", bd=1, relief="solid", padx=10, pady=5)
    stats.pack(fill="x", padx=40)

    r1 = tk.Frame(stats, bg="#f9f9f9")
    r1.pack(fill="x")
    tk.Label(r1, text="Time:", font=("Arial", 10, "bold"), bg="#f9f9f9").pack(side="left")
    t_lbl = tk.Label(r1, text="0s", font=("Arial", 10), bg="#f9f9f9", fg="blue")
    t_lbl.pack(side="right")

    r2 = tk.Frame(stats, bg="#f9f9f9")
    r2.pack(fill="x")
    tk.Label(r2, text="Steps:", font=("Arial", 10, "bold"), bg="#f9f9f9").pack(side="left")
    s_lbl = tk.Label(r2, text="0", font=("Arial", 10), bg="#f9f9f9", fg="blue")
    s_lbl.pack(side="right")


    p_lbl = tk.Label(parent, text="Step: 0", font=("Arial", 12), bg="white", fg="#666")
    p_lbl.pack(pady=(15, 5))


    g_cont = tk.Frame(parent, bg="white")
    g_cont.pack(pady=5)
    labels = []
    for r in range(3):
        for c in range(3):
            l = tk.Label(g_cont, text="?", font=("Helvetica", 24, "bold"), width=4, height=2, bg="#e0e0e0", fg="#333",
                         relief="flat")
            l.grid(row=r, column=c, padx=3, pady=3)
            labels.append(l)


    nav = tk.Frame(parent, bg="white")
    nav.pack(pady=20)
    tk.Button(nav, text="◄ Prev", command=prev_cmd, bg="white", relief="groove").pack(side="left", padx=10)
    tk.Button(nav, text="Next ►", command=next_cmd, bg="white", relief="groove").pack(side="left", padx=10)

    return t_lbl, s_lbl, p_lbl, labels



lbl_time_A, lbl_steps_A, lbl_prog_A, grid_labels_A = create_solver_panel(
    frame_A, "Greedy Algorithm", None, None, None, prev_A, next_A
)


lbl_time_B, lbl_steps_B, lbl_prog_B, grid_labels_B = create_solver_panel(
    frame_B, "A* Algorithm", None, None, None, prev_B, next_B
)


root.mainloop()
