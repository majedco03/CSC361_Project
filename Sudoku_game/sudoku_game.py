import copy
import random
import math
import time
import statistics

# Check for numpy (Required for the SA algorithm)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class SudokuGame:
    """
    Handles Game Logic.
    Now includes a FIXED version of the user's Simulated Annealing.
    """
    def __init__(self): 
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original_board = [] 
        self.steps = 0      
        self.backtracks = 0 
        
    def generate_puzzle(self, difficulty_level=0.5):
        try:
            from sudoku import Sudoku
            seed = random.randint(0, 1000000000)
            try:
                puzzle = Sudoku(3, seed=seed).difficulty(difficulty_level)
            except TypeError:
                puzzle = Sudoku(3).difficulty(difficulty_level)
            raw_board = puzzle.board
            self.board = [[0 if val is None else val for val in row] for row in raw_board]
        except Exception:
            self.board = self.internal_generate(difficulty_level)

        self.original_board = copy.deepcopy(self.board)
        self.steps = 0
        self.backtracks = 0
        return self.board

    def internal_generate(self, difficulty):
        board = [[0]*9 for _ in range(9)]
        for i in range(0, 9, 3): self.fill_box(board, i, i)
        self.solve_internal(board)
        attempts = int(difficulty * 64) + 20 
        while attempts > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                attempts -= 1
        return board

    def fill_box(self, board, row, col):
        for i in range(3):
            for j in range(3):
                while True:
                    num = random.randint(1, 9)
                    if not self.used_in_box(board, row, col, num): break
                board[row + i][col + j] = num

    def used_in_box(self, board, row_start, col_start, num):
        for i in range(3):
            for j in range(3):
                if board[row_start + i][col_start + j] == num: return True
        return False

    def solve_internal(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_safe(board, i, j, num):
                            board[i][j] = num
                            if self.solve_internal(board): return True
                            board[i][j] = 0
                    return False
        return True
    
    # --- CSP HELPER FUNCTIONS ---
    def is_safe(self, board, row, col, num):
        for x in range(9):
            if board[row][x] == num: return False
            if board[x][col] == num: return False
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num: return False
        return True

    def find_empty_naive(self, board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0: return (r, c)
        return None

    def find_mrv_cell(self, board):
        min_count = 10
        mrv_cell = None
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    legal_moves = 0
                    for num in range(1, 10):
                        if self.is_safe(board, r, c, num): legal_moves += 1
                    if legal_moves < min_count:
                        min_count = legal_moves
                        mrv_cell = (r, c)
                        if min_count <= 1: return mrv_cell
        return mrv_cell

    # --- ALGORITHM 1: NAIVE BACKTRACKING ---
    def solve_naive_generator(self):
        empty_spot = self.find_empty_naive(self.board)
        if not empty_spot: return True
        row, col = empty_spot
        for num in range(1, 10):
            if self.is_safe(self.board, row, col, num):
                self.board[row][col] = num
                self.steps += 1
                yield (row, col, num, self.steps, self.backtracks)
                result = yield from self.solve_naive_generator()
                if result is True: return True
                self.board[row][col] = 0
                self.backtracks += 1
                yield (row, col, 0, self.steps, self.backtracks)
        return False

    # --- ALGORITHM 2: SMART CSP (MRV) ---
    def solve_csp_generator(self):
        empty_spot = self.find_mrv_cell(self.board)
        if not empty_spot: return True
        row, col = empty_spot
        for num in range(1, 10):
            if self.is_safe(self.board, row, col, num):
                self.board[row][col] = num
                self.steps += 1
                yield (row, col, num, self.steps, self.backtracks)
                result = yield from self.solve_csp_generator()
                if result is True: return True
                self.board[row][col] = 0
                self.backtracks += 1
                yield (row, col, 0, self.steps, self.backtracks)
        return False

    # =================================================================
    # --- ALGORITHM 3: SIMULATED ANNEALING 
    # =================================================================

    def CreateList3x3Blocks(self):
        finalListOfBlocks = []
        for r in range (0,9):
            tmpList = []
            block1 = [i + 3*((r)%3) for i in range(0,3)]
            block2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
            for x in block1:
                for y in block2:
                    tmpList.append([x,y])
            finalListOfBlocks.append(tmpList)
        return(finalListOfBlocks)

    def RandomlyFill3x3Blocks(self, sudoku, listOfBlocks):
        for block in listOfBlocks:
            for box in block:
                if sudoku[box[0],box[1]] == 0:
                    # Identify existing numbers in this block to avoid duplicates
                    existing = []
                    for r_i in range(block[0][0], block[-1][0]+1):
                        for c_i in range(block[0][1], block[-1][1]+1):
                             if sudoku[r_i, c_i] != 0:
                                 existing.append(sudoku[r_i, c_i])
                    
                    possible = [i for i in range(1, 10) if i not in existing]
                    if possible:
                        sudoku[box[0],box[1]] = random.choice(possible)
                    else:
                        sudoku[box[0],box[1]] = random.randint(1,9)
        return sudoku

    def CalculateNumberOfErrorsRowColumn(self, row, column, sudoku):
        numberOfErrors = (9 - len(np.unique(sudoku[:,column]))) + (9 - len(np.unique(sudoku[row,:])))
        return(numberOfErrors)

    def CalculateNumberOfErrors(self, sudoku):
        numberOfErrors = 0 
        for i in range (0,9):
            numberOfErrors += self.CalculateNumberOfErrorsRowColumn(i ,i ,sudoku)
        return(numberOfErrors)

    def TwoRandomBoxesWithinBlock(self, fixedSudoku, block):
        # Safety: Ensure there are at least 2 mutable cells to swap
        mutable_boxes = [box for box in block if fixedSudoku[box[0], box[1]] != 1]
        
        if len(mutable_boxes) < 2:
            # Cannot swap if less than 2 mutable cells. Return indices that won't change anything.
            return [block[0], block[0]]

        return random.sample(mutable_boxes, 2)

    def ProposedState(self, sudoku, fixedSudoku, listOfBlocks):
        randomBlock = random.choice(listOfBlocks)
        boxesToFlip = self.TwoRandomBoxesWithinBlock(fixedSudoku, randomBlock)
        
        proposedSudoku = np.copy(sudoku)
        placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
        proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
        proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
        
        return([proposedSudoku, boxesToFlip])

    def CalculateInitialSigma(self, sudoku, fixedSudoku, listOfBlocks):
        listOfDifferences = []
        tmpSudoku = np.copy(sudoku)
        for i in range(1, 10):
            res = self.ProposedState(tmpSudoku, fixedSudoku, listOfBlocks)
            tmpSudoku = res[0]
            listOfDifferences.append(self.CalculateNumberOfErrors(tmpSudoku))
        
        if len(listOfDifferences) > 1:
            return (statistics.pstdev(listOfDifferences))
        return 1.0

    def ChooseNumberOfItterations(self, fixed_sudoku):
        numberOfItterations = 0
        for i in range (0,9):
            for j in range (0,9):
                if fixed_sudoku[i,j] != 0:
                    numberOfItterations += 1
        return numberOfItterations

    def solve_annealing_generator(self):
        """
        Runs the User's Simulated Annealing logic (Fixed).
        Yields state updates for the GUI.
        """
        if not NUMPY_AVAILABLE:
            print("Error: Numpy not installed. Cannot run SA.")
            return False

        # 1. Setup Data Structures
        sudoku = np.array(self.board)
        fixedSudoku = np.copy(sudoku)
        
        # Mark fixed cells (1 = fixed, 0 = mutable)
        for i in range(9):
            for j in range(9):
                if fixedSudoku[i,j] != 0: 
                    fixedSudoku[i,j] = 1
                else:
                    fixedSudoku[i,j] = 0
        
        listOfBlocks = self.CreateList3x3Blocks()
        
        # 2. Random Fill (Valid 3x3 Blocks)
        tmpSudoku = self.RandomlyFill3x3Blocks(sudoku, listOfBlocks)
        
        # Visual Sync: Update GUI with initial random state
        for r in range(9):
            for c in range(9):
                if self.original_board[r][c] == 0:
                    self.board[r][c] = int(tmpSudoku[r,c])
                    yield (r, c, int(tmpSudoku[r,c]), 0, 0)
        
        sigma = self.CalculateInitialSigma(sudoku, fixedSudoku, listOfBlocks)
        score = self.CalculateNumberOfErrors(tmpSudoku)
        itterations = self.ChooseNumberOfItterations(fixedSudoku)
        
        solutionFound = 0
        if score <= 0: solutionFound = 1
        
        decreaseFactor = 0.99
        stuckCount = 0
        step_count = 0
        
        # 3. Main Loop
        while solutionFound == 0:
            previousScore = score
            
            for i in range(0, itterations):
                step_count += 1
                
                # Propose New State
                proposal = self.ProposedState(tmpSudoku, fixedSudoku, listOfBlocks)
                newSudoku = proposal[0]
                boxesToCheck = proposal[1]
                
                # Calculate Cost
                currentCost = self.CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], tmpSudoku) + \
                              self.CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], tmpSudoku)
                newCost = self.CalculateNumberOfErrorsRowColumn(boxesToCheck[0][0], boxesToCheck[0][1], newSudoku) + \
                          self.CalculateNumberOfErrorsRowColumn(boxesToCheck[1][0], boxesToCheck[1][1], newSudoku)
                
                costDifference = newCost - currentCost
                
                # Metropolis Acceptance Criterion
                rho = math.exp(-costDifference/sigma) if sigma > 0 else 0
                
                if(np.random.uniform(1,0,1) < rho):
                    # Accept Change
                    tmpSudoku = newSudoku
                    score += costDifference
                    
                    # Visual Sync: Update swapped cells on GUI
                    r1, c1 = boxesToCheck[0]
                    r2, c2 = boxesToCheck[1]
                    val1 = int(tmpSudoku[r1, c1])
                    val2 = int(tmpSudoku[r2, c2])
                    
                    self.board[r1][c1] = val1
                    self.board[r2][c2] = val2
                    
                    yield (r1, c1, val1, step_count, score)
                    yield (r2, c2, val2, step_count, score)
                    
                    if score <= 0:
                        solutionFound = 1
                        break

            # Cooling Schedule
            sigma *= decreaseFactor
            if score <= 0:
                solutionFound = 1
                break
                
            # Stuck Logic
            if score >= previousScore:
                stuckCount += 1
            else:
                stuckCount = 0
            if (stuckCount > 80):
                sigma += 2
            
            # Keep GUI alive
            yield (-1, -1, 0, step_count, score)

        return True

    # --- BATCH ANALYSIS TOOL ---
    def run_batch_analysis(self, algorithm_name, trials=10):
        total_time = 0
        success_count = 0
        
        for _ in range(trials):
            self.board = [row[:] for row in self.original_board]
            self.steps = 0
            
            start = time.perf_counter()
            
            if "Smart" in algorithm_name:
                gen = self.solve_csp_generator()
            elif "Naive" in algorithm_name:
                gen = self.solve_naive_generator()
            else:
                gen = self.solve_annealing_generator()

            try:
                while True:
                    next(gen)
            except StopIteration:
                pass 
            except Exception:
                pass
                
            end = time.perf_counter()
            success_count += 1
            total_time += (end - start)
            
        avg_time = total_time / trials if trials > 0 else 0
        
        return {
            "algo": algorithm_name,
            "trials": trials,
            "success_rate": f"{success_count}/{trials}",
            "avg_time": f"{avg_time:.4f}s",
            "avg_steps": "N/A"
        }
