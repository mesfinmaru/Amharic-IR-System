# 
import tkinter as tk
from gui.app import AmharicIRGUI

def main():

    root = tk.Tk()
    app = AmharicIRGUI(root)

    root.geometry("1200x700")
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()