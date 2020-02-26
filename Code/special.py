from tkinter import *
import time

## Hides the parent window and runs the recursive function described below
## When the child window is closed, the position of the parent window
## is changed to where the child window was and is shown again
def RunCheck(master, root):
    master.withdraw()
    closed = False
    x = 0
    y = 0
    while not closed:
        try:
            x = root.winfo_x()
            y = root.winfo_y()
        except:
            pass
        closed = CheckIfClosed(0, root)

    if closed:
        master.geometry("+{}+{}".format(x,y))
        master.deiconify()


## Checks recursively to see if the currently active window has been closed or
## not. If the window is still open and 1 second has passed, the function returns
## False. If the window is closed, the function returns True. Otherwise, the window
## is updated, the function waits for 10ms then executes itself again, with an
## incremented 'count' argument
def CheckIfClosed(count, root):
    if Toplevel.winfo_exists(root) and count == 100:
        return False
    elif not Toplevel.winfo_exists(root):
        return True
    else:
        root.update()
        time.sleep(0.01)
        CheckIfClosed(count+1, root)
