import tkinter as tk
from tkinter import messagebox, ttk
from copy import deepcopy
from collections import deque
import time

class SudokuCSP:
    def __init__(self, board):
        """
        Initialize Sudoku CSP solver.
        board: 9x9 list of integers (0 represents empty cell)
        """
        self.size = 9
        self.box_size = 3
        self.board = board
        self.domains = {}
        self.initialize_domains()
        self.nodes_explored = 0
        
    def initialize_domains(self):
        """Initialize domains for each variable (cell)"""
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    self.domains[(i, j)] = set(range(1, 10))
                else:
                    self.domains[(i, j)] = {self.board[i][j]}
    
    def get_row(self, row):
        return [self.board[row][col] for col in range(self.size)]
    
    def get_col(self, col):
        return [self.board[row][col] for row in range(self.size)]
    
    def get_box(self, row, col):
        start_row = (row // self.box_size) * self.box_size
        start_col = (col // self.box_size) * self.box_size
        box = []
        for i in range(start_row, start_row + self.box_size):
            for j in range(start_col, start_col + self.box_size):
                box.append(self.board[i][j])
        return box
    
    def get_peers(self, row, col):
        peers = set()
        for c in range(self.size):
            if c != col:
                peers.add((row, c))
        for r in range(self.size):
            if r != row:
                peers.add((r, col))
        start_row = (row // self.box_size) * self.box_size
        start_col = (col // self.box_size) * self.box_size
        for i in range(start_row, start_row + self.box_size):
            for j in range(start_col, start_col + self.box_size):
                if i != row and j != col:
                    peers.add((i, j))
        return peers
    
    def is_consistent(self, row, col, value):
        for c in range(self.size):
            if self.board[row][c] == value and c != col:
                return False
        for r in range(self.size):
            if self.board[r][col] == value and r != row:
                return False
        start_row = (row // self.box_size) * self.box_size
        start_col = (col // self.box_size) * self.box_size
        for i in range(start_row, start_row + self.box_size):
            for j in range(start_col, start_col + self.box_size):
                if self.board[i][j] == value and (i != row or j != col):
                    return False
        return True
    
    def ac3(self):
        queue = deque()
        for i in range(self.size):
            for j in range(self.size):
                for peer in self.get_peers(i, j):
                    queue.append(((i, j), peer))
        
        while queue:
            (x, y) = queue.popleft()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for peer in self.get_peers(x[0], x[1]):
                    if peer != y:
                        queue.append((peer, x))
        return True
    
    def revise(self, x, y):
        revised = False
        y_domain = self.domains[y]
        if len(y_domain) == 1:
            y_value = next(iter(y_domain))
            if y_value in self.domains[x]:
                self.domains[x].remove(y_value)
                revised = True
        return revised
    
    def forward_checking(self, row, col, value):
        saved_domains = deepcopy(self.domains)
        for peer in self.get_peers(row, col):
            if value in self.domains[peer]:
                self.domains[peer].remove(value)
                if len(self.domains[peer]) == 0:
                    self.domains = saved_domains
                    return None
        return saved_domains
    
    def get_next_empty_cell(self):
        min_domain_size = float('inf')
        best_cell = None
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    domain_size = len(self.domains[(i, j)])
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        best_cell = (i, j)
                        if min_domain_size == 1:
                            return best_cell
        return best_cell
    
    def backtrack(self, use_forward_checking=True, use_ac3=True, callback=None):
        self.nodes_explored += 1
        if use_ac3:
            if not self.ac3():
                return False
        empty_cell = self.get_next_empty_cell()
        if empty_cell is None:
            return True
        row, col = empty_cell
        for value in sorted(self.domains[(row, col)]):
            if self.is_consistent(row, col, value):
                self.board[row][col] = value
                if use_forward_checking:
                    saved_domains = self.forward_checking(row, col, value)
                    if saved_domains is None:
                        self.board[row][col] = 0
                        continue
                else:
                    saved_domains = None
                if callback:
                    callback(row, col, value)
                if self.backtrack(use_forward_checking, use_ac3, callback):
                    return True
                self.board[row][col] = 0
                if saved_domains is not None:
                    self.domains = saved_domains
                if callback:
                    callback(row, col, 0)
        return False
    
    def solve(self, method='all', callback=None):
        self.initialize_domains()
        self.nodes_explored = 0
        start_time = time.time()
        if method == 'bt':
            solved = self.backtrack(use_forward_checking=False, use_ac3=False, callback=callback)
        elif method == 'fc':
            solved = self.backtrack(use_forward_checking=True, use_ac3=False, callback=callback)
        elif method == 'ac3':
            solved = self.backtrack(use_forward_checking=False, use_ac3=True, callback=callback)
        else:
            solved = self.backtrack(use_forward_checking=True, use_ac3=True, callback=callback)
        end_time = time.time()
        return solved, end_time - start_time, self.nodes_explored


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku CSP")
        self.root.geometry("500x620")
        self.root.configure(bg='#f0f0f0')
        
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.solver_method = tk.StringVar(value="all")
        
        self.setup_ui()
        
    def setup_ui(self):
        title_label = tk.Label(self.root, text="Sudoku CSP Solver", 
                               font=("Arial", 18, "bold"), 
                               bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=5)
        
        grid_frame = tk.Frame(self.root, bg='#f0f0f0')
        grid_frame.pack(pady=10)
        
        for i in range(9):
            for j in range(9):
                border_width = 2 if i % 3 == 0 or j % 3 == 0 else 1
                self.entries[i][j] = tk.Entry(grid_frame, width=2, font=("Arial", 14, "bold"),
                                              justify='center', bg='white', fg='#2c3e50',
                                              relief='solid', bd=border_width)
                self.entries[i][j].grid(row=i, column=j, padx=1, pady=1)
                self.entries[i][j].bind('<KeyRelease>', lambda e, row=i, col=j: self.validate_input(row, col))
        
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=5)
        
        method_frame = tk.LabelFrame(control_frame, text="Method", 
                                     font=("Arial", 9, "bold"), bg='#f0f0f0')
        method_frame.grid(row=0, column=0, padx=5, sticky='w')
        
        methods = [("Backtrack", "bt"), ("+ FC", "fc"), ("+ AC3", "ac3"), ("Full CSP", "all")]
        for text, value in methods:
            tk.Radiobutton(method_frame, text=text, variable=self.solver_method, 
                           value=value, bg='#f0f0f0', font=("Arial", 9)).pack(anchor='w')
        
        button_frame = tk.Frame(control_frame, bg='#f0f0f0')
        button_frame.grid(row=0, column=1, padx=5)
        
        preset_frame = tk.Frame(button_frame, bg='#f0f0f0')
        preset_frame.pack()
        
        for diff, color in [('easy', '#27ae60'), ('medium', '#f39c12'), ('hard', '#e74c3c'), ('veryhard', '#8e44ad')]:
            btn = tk.Button(preset_frame, text=diff.capitalize(), command=lambda d=diff: self.load_preset(d),
                            bg=color, fg='white', font=("Arial", 8, "bold"), width=7)
            btn.pack(side='left', padx=2, pady=2)
            
        action_frame = tk.Frame(button_frame, bg='#f0f0f0')
        action_frame.pack(pady=5)
        
        tk.Button(action_frame, text="Solve", command=self.solve_puzzle, bg='#3498db', fg='white', 
                  font=("Arial", 10, "bold"), width=10).pack(side='left', padx=2)
        tk.Button(action_frame, text="Clear", command=self.clear_board, bg='#95a5a6', fg='white', 
                  font=("Arial", 10, "bold"), width=10).pack(side='left', padx=2)
        
        status_frame = tk.Frame(self.root, bg='#f0f0f0', relief='sunken', bd=1)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready", font=("Arial", 9), bg='#f0f0f0')
        self.status_label.pack()
        self.stats_label = tk.Label(status_frame, text="", font=("Arial", 8), bg='#f0f0f0', fg='#7f8c8d')
        self.stats_label.pack()

    def validate_input(self, row, col):
        value = self.entries[row][col].get()
        if len(value) > 1:
            self.entries[row][col].delete(1, tk.END)
        elif value and (not value.isdigit() or int(value) < 1 or int(value) > 9):
            self.entries[row][col].delete(0, tk.END)
    
    def get_board(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                board[i][j] = int(val) if val.isdigit() else 0
        return board
    
    def set_board(self, board):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                if board[i][j] != 0:
                    self.entries[i][j].insert(0, str(board[i][j]))
                    self.entries[i][j].config(fg='#e74c3c')
                else:
                    self.entries[i][j].config(fg='#2c3e50')
    
    def clear_board(self):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].config(fg='#2c3e50')
        self.status_label.config(text="Cleared")
    
    def load_preset(self, difficulty):
        puzzles = {
            'easy': [[0,0,4,0,3,0,0,5,0],[6,0,9,4,0,0,0,0,0],[0,0,5,1,0,0,4,8,9],[0,0,0,0,6,0,9,3,0],[3,0,0,8,0,7,0,0,2],[0,2,6,0,4,0,0,0,0],[4,5,3,0,0,9,6,0,0],[0,0,0,0,0,4,7,0,5],[0,9,0,0,5,0,2,0,0]],
            'medium': [[0,1,2,4,0,0,0,7,0],[0,0,8,0,0,0,0,0,0],[0,0,9,5,0,0,0,3,0],[0,0,0,6,7,0,9,0,0],[5,4,0,0,0,0,0,2,0],[0,6,4,5,0,0,0,0,0],[7,8,0,3,4,0,0,0,0],[0,0,0,1,0,0,0,0,0],[2,0,0,6,5,9,0,0,0]],
            'hard': [[0,1,2,4,0,0,0,7,0],[0,0,6,0,0,4,3,0,0],[0,0,0,3,0,0,0,6,0],[3,8,0,7,6,0,0,0,0],[2,7,0,1,5,0,0,0,0],[0,0,0,2,0,0,0,5,0],[7,0,1,0,2,0,0,0,0],[8,0,0,9,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
            'veryhard': [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,3,0,8,5],[0,0,1,0,2,0,0,0,0],[0,0,0,5,0,7,0,0,0],[0,0,4,0,0,0,1,0,0],[0,9,0,0,0,0,0,0,0],[5,0,0,0,0,0,0,7,3],[0,0,2,0,1,0,0,0,0],[0,0,0,0,4,0,0,0,9]]
        }
        self.clear_board()
        self.set_board(puzzles.get(difficulty, puzzles['easy']))
        self.status_label.config(text=f"Loaded {difficulty}")

    def update_cell_callback(self, row, col, value):
        def update():
            self.entries[row][col].delete(0, tk.END)
            if value != 0:
                self.entries[row][col].insert(0, str(value))
                self.entries[row][col].config(fg='#27ae60')
            self.root.update()
            time.sleep(0.005)
        self.root.after(0, update)

    def solve_puzzle(self):
        board = self.get_board()
        if not self.is_valid_board(board):
            messagebox.showerror("Error", "Board has conflicts!")
            return
        solver = SudokuCSP(board)
        method = self.solver_method.get()
        self.status_label.config(text="Solving...")
        solved, solve_time, nodes = solver.solve(method, self.update_cell_callback)
        if solved:
            self.set_board(solver.board)
            self.status_label.config(text=f"Solved in {solve_time:.3f}s")
            self.stats_label.config(text=f"Nodes: {nodes}")
        else:
            self.status_label.config(text="No solution!")

    def is_valid_board(self, board):
        for i in range(9):
            row = [board[i][j] for j in range(9) if board[i][j] != 0]
            if len(row) != len(set(row)): return False
            col = [board[j][i] for j in range(9) if board[j][i] != 0]
            if len(col) != len(set(col)): return False
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box = [board[i][j] for i in range(br, br+3) for j in range(bc, bc+3) if board[i][j] != 0]
                if len(box) != len(set(box)): return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()
