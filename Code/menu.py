from tkinter import *
import simulation
import question
from threading import *
import special

class MainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Box-on-a-slope Physics Simulator - Main Menu")
        self.master.geometry("500x500+100+200")

        self.SimMenuRoot = None
        self.LoginWindowRoot = None

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(5, weight=1)

        Label(self.master, text="Menu", font=("AbcPrint",20)).grid(row=0, column=1)
        Button(self.master, text="Run Simulation", command=self.StartSimMenu).grid(row=2,column=1, pady=5)
        Button(self.master, text="Login", padx=26, command=self.StartLoginWindow).grid(row=3, column=1, pady=5)
        Button(self.master, text="Exit", padx=32, command=self.Exit).grid(row=4, column=1, pady=5)

    def StartSimMenu(self):
        if self.SimMenuRoot != None and Toplevel.winfo_exists(self.SimMenuRoot):
            self.SimMenuRoot.destroy()
        self.SimMenuRoot = Toplevel(self.master)
        self.SimMenuRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.SimMenuRoot))
        t.start()
        self.SimMenu = simulation.MainWindow(self.SimMenuRoot)

    def StartLoginWindow(self):
        if self.LoginWindowRoot != None and Toplevel.winfo_exists(self.LoginWindowRoot):
            self.LoginWindowRoot.destroy()
        
        self.LoginWindowRoot = Toplevel(self.master)
        self.LoginWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.LoginWindowRoot))
        t.start()
        self.LoginWindow = question.LoginWindow(self.LoginWindowRoot)

    def Exit(self):
        self.master.destroy()
        
Root = Tk()
GUI = MainMenu(Root)
Root.mainloop()
