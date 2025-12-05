class Connect4App:
    #just run the gui
    def __init__(self):
        import tkinter as tk
        from connect4_gui import Connect4GUI

        root = tk.Tk()
        self.gui = Connect4GUI(root)
        root.mainloop()

if __name__ == "__main__":
    Connect4App()