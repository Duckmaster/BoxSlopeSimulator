from tkinter import *
from tkinter import filedialog
from math import radians, degrees, sin, cos, tan, atan, sqrt
from datetime import datetime
import time
import pickle as p

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Box-on-a-slope Physics Simulator - Simulation Window")
        self.master.geometry("500x500")

        self.NewWindow = None

        self.Angle = StringVar(value="0")
        self.Mass = StringVar(value="0")
        self.Gravity = StringVar(value="0")
        self.FrictionConst = StringVar(value="0")
        self.FrictionCheck = BooleanVar()
        Label(self.master, text="Angle to horizontal: ").grid(row=0)
        Label(self.master, text="Mass (kg): ").grid(row=1)
        Label(self.master, text="Gravity (N): ").grid(row=2)
        Label(self.master, text="Frictional coefficient: ").grid(row=3)
        Checkbutton(self.master, text="Friction?", variable=self.FrictionCheck,
                                            command=self.ToggleFriction).grid(row=3, column=2)
        Entry(self.master, textvariable=self.Angle).grid(row=0, column=1)
        Entry(self.master, textvariable=self.Mass).grid(row=1, column=1)
        Entry(self.master, textvariable=self.Gravity).grid(row=2, column=1)
        self.FrictionEntry = Entry(self.master, textvariable=self.FrictionConst, state=DISABLED)
        self.FrictionEntry.grid(row=3, column=1)
        self.ErrorLabel = Label(self.master, text="", fg="RED")
        self.ErrorLabel.grid(row=0, column=2)
        
        SimButton = Button(self.master, text="Start Simulation", command=self.Start_Sim).grid(row=4)
        ExitButton = Button(self.master, text="Exit", command=self.Exit).grid(row=5)

        menubar = Menu(self.master)
        self.fileName = ""
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Load simulation", command=self.LoadSim)
        fileMenu.add_command(label="Save simulation", command=self.SaveSim)
        menubar.add_cascade(label="File", menu=fileMenu)

        self.master.config(menu=menubar)


    def Start_Sim(self):
        if self.NewWindow != None and Toplevel.winfo_exists(self.NewWindow):
            self.NewWindow.destroy()
        if not self.isValidNum(self.Angle.get()):
            self.ErrorLabel['text'] = "Angle cannot contain non-numeric characters"
        elif float(self.Angle.get()) > 45:
            self.ErrorLabel['text'] = "Angle cannot be larger than 45 degrees"
        elif float(self.Angle.get()) <= 0:
            self.ErrorLabel['text'] = "Angle cannot be 0 degrees or less"
        elif not self.isValidNum(self.Mass.get()):
            self.ErrorLabel['text'] = "Mass cannot contain non-numeric characters"
        elif float(self.Mass.get()) <= 0:
            self.ErrorLabel['text'] = "Mass cannot be 0 or less"
        elif not self.isValidNum(self.Gravity.get()):
            self.ErrorLabel['text'] = "Gravity cannot contain non-numeric characters"
        elif float(self.Gravity.get()) < 0:
            self.ErrorLabel['text'] = "Gravity cannot be 0 or less"
        elif not self.isValidNum(self.FrictionConst.get()):
            self.ErrorLabel['text'] = "Friction cannot contain non-numeric characters"
        elif float(self.FrictionConst.get()) < 0 or float(self.FrictionConst.get()) >= 1:
            self.ErrorLabel['text'] = "Friction coefficient must be between 0 and 1"
        else:
            if self.ErrorLabel['text'] != "":
                self.ErrorLabel['text'] = ""
            if self.Angle.get()[0] == "0":
                self.Angle.set(self.Angle.get().lstrip("0"))
            Values = (float(self.Angle.get()), float(self.Mass.get()), float(self.Gravity.get()),
                      float(self.FrictionConst.get()), self.FrictionCheck.get())
            self.NewWindow = Toplevel(self.master)
            self.NewWindow.attributes("-topmost", True)
            simWindow = SimWindow(self.NewWindow, Values)

    def ToggleFriction(self):
        if self.FrictionCheck.get():
            self.FrictionEntry["state"] = NORMAL
        else:
            self.FrictionEntry["state"] = DISABLED
            self.FrictionConst.set(0)
            
    def SaveSim(self):
        angle = self.Angle.get()
        mass = self.Mass.get()
        gravity = self.Gravity.get()
        if self.FrictionCheck.get():
            friction = self.FrictionConst.get()
        else:
            friction = 0
        filepath = filedialog.asksaveasfilename(filetypes=(("Simulation file", "*.sim"),
                                                           ("All files","*.*"),))
        if filepath[-4:] != ".sim":
            filepath += ".sim"

        filewriter = open(filepath, "wb")
        p.dump((angle, mass, gravity, friction), filewriter)
        filewriter.close()

    def LoadSim(self):
        vals = [self.Angle, self.Mass, self.Gravity, self.FrictionConst]
        filepath = filedialog.askopenfilename(filetypes=(("Simulation file", "*.sim"),))
        if filepath == "":
            return False
        filereader = open(filepath, "rb")
        data = p.load(filereader)
        filereader.close()
        data = tuple(data)
        for i in range(len(vals)):
            vals[i].set(data[i])
            if i == 3 and data[i] != 0:
                self.FrictionCheck.set(1)
                self.ToggleFriction()
            elif i == 3 and data[i] == 0:
                self.FrictionCheck.set(0)
                self.ToggleFriction()

    def isValidNum(self,num):
        try:
            float(num)
            return True
        except:
            return False
            
    def Exit(self):
        self.master.destroy()

class SimWindow:
    def __init__(self, master, values):
        self.master = master
        self.master.title("Simulation Window")
        self.master.geometry("850x650")
        self.master.resizable(width=False, height=False)
        angle = values[0]
        angleStr = str(round(values[0]))
        self.Gradient = (tan(radians(int(angleStr))))
        self.canvas = Canvas(self.master, width=650, height=650, bg="#D6D6D6")
        self.canvas.pack(side=LEFT)
        self.TestLabel = Label(self.master, text=("Gradient:",str(round(self.Gradient, 3))))
        self.TestLabel.pack()
        Label(self.master, text=("Weight:", str(values[1]*values[2])+"N"), fg="red").pack()

        self.ExitButton = Button(self.master, text="Exit", command=self.CloseWindow)
        self.ExitButton.pack(side=BOTTOM, pady=10)
        
        self.lines = {}
        self.boxes = {}

        self.slopeLine = Line("sL", [0, 0], [600, 645], "black", self.DrawLine, self.EraseLine)
        calcStartY(self.slopeLine, self.Gradient)
        self.slopeLine.DrawMe()

        self.parallelSlope = Line("pSL", [0, 50], [650, self.slopeLine.endPoint[1]-50], "blue", self.DrawLine, self.EraseLine)
        calcStartY(self.parallelSlope, self.Gradient)

        self.buttonState = BooleanVar()
        self.buttonState.set(1)

        self.box = Box("b1", self.slopeLine.startPoint, self.slopeLine.endPoint, self.Gradient, "black",
                       self.DrawBox, self.EraseBox, values[1], self.canvas, self.slopeLine, values[2],
                       self.buttonState, values[3], values[4], self.SliderVal)
        
        self.box.calcBoxCoords(self.parallelSlope)
        self.box.CalcVals()
        
        self.distanceLabel = Label(self.master, text=("Distance:",str(round(self.box.distance,2))+"m"))
        self.distanceLabel.pack()
        self.timeLabel = Label(self.master, text=("Time:", str(round(self.box.time, 2))+"s"))
        self.timeLabel.pack()
        self.accLabel = Label(self.master, text=("Acceleration:", str(round(self.box.acceleration, 3))+"ms^-2"))
        self.accLabel.pack()
        self.velLabel = Label(self.master, text=("Velocity:", str(round(self.box.finalV, 3))+"ms^-1"))
        self.velLabel.pack()
        var = ("Reaction force: "+str(round(self.box.reactionForce, 2))+"N")
        Label(self.master, text=var, fg="green").pack()
        Label(self.master, text=("Friction:", str(round(self.box.friction, 2))+"N"), fg="blue").pack()
        
        Button(self.master, text="Start/stop", command=self.TogglePlay).pack()

        self.Slider = Scale(self.master, from_=0, to=5, orient=HORIZONTAL)
        self.Slider.pack()

        self.buttonRestart = Button(self.master, text="Restart Sim",
                                    command=self.RestartSim)
        self.buttonRestart.pack()
        

        self.box.StartMove(self.boxes, self.velLabel)
        self.buttonRestart["state"] = NORMAL
        

    def DrawLine(self, ident, startPoint, endPoint, colour):
        self.lines[ident] = self.canvas.create_line(startPoint, endPoint, fill=colour)

    def EraseLine(self, ident):
        self.canvas.delete(self.lines[ident])

    def DrawBox(self, ident, coords, colour):
        self.boxes[ident] = self.canvas.create_polygon(coords, fill=colour)
    
    def EraseBox(self, ident):
        self.canvas.delete(self.boxes[ident])

    def CloseWindow(self):
        self.master.destroy()

    def RemoveBox(self, ident):
        self.canvas.delete(ident)

    def TogglePlay(self):
        if self.buttonState.get() == 0:
            self.buttonState.set(1)
        else:
            self.buttonState.set(0)

    def SliderVal(self):
        return self.Slider.get()

    def RestartSim(self):
        ## Erase the box from the canvas
        self.box.EraseMe()

        ## Reset the key values of the box so simulation behaves as expected
        self.box.distanceTotal = 0
        self.box.startV = 0
        self.box.finalV = 0
        self.box.calcBoxCoords(self.parallelSlope)
        self.box.CalcVals()

        ## Stop the box by default and start it moving
        self.buttonState.set(1)
        self.box.StartMove(self.boxes, self.velLabel)

class Line:
    def __init__(self, ident, startPoint, endPoint, colour, drawFunc, eraseFunc):
        self.ident = ident
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.colour = colour
        self.drawFunc = drawFunc
        self.eraseFunc = eraseFunc
        self.intercept = 0

    def DrawMe(self):
        self.drawFunc(self.ident, self.startPoint, self.endPoint, self.colour)

    def EraseMe(self):
        self.eraseFunc(self.ident)

    def calcYCoord(self, x, m):
        yCoord = (float(m) * int(x)) + self.intercept
        return yCoord

class Box(Line):
    def __init__(self, ident, startPoint, endPoint, #coords
                 gradient, colour, drawFunc, eraseFunc, mass,
                 canvas, slopeLine, gravity, buttonstate,
                 frictionConst, frictionEnabled, getSliderVal):
        Line.__init__(self, ident, startPoint, endPoint, colour, drawFunc, eraseFunc) #INHERTS FROM LINE CLASS
        self.currentCoords = []
        self.Gradient = gradient
        self.Angle = degrees(atan(self.Gradient))
        self.timeDelay = 10/1000

        self.startV = 0
        self.finalV = 0
        self.s = 0
        self.lineSeg = 0
        self.mass = mass
        self.weight = mass * gravity
        self.acceleration = 0
        self.distance = 0
        self.time = 0
        self.reactionForce = 0
        self.distanceTotal = 0

        self.slopeLine = slopeLine

        self.canvas = canvas

        self.reachedEnd = False

        self.distances, self.velocities = (None, None)

        self.incCount = 0
        self.maxCount = 0

        self.buttonState = buttonstate
        self.frictionConst = frictionConst
        self.frictionEnabled = frictionEnabled
        self.friction = 0

        self.sliderVal = getSliderVal
        
    def DrawMe(self):
        self.drawFunc(self.ident, self.currentCoords, self.colour)

    def EraseMe(self):
        self.eraseLabels()
        self.eraseFunc(self.ident)
    
    def UpdateCoords(self, val):
        if self.endPoint > [round(self.currentCoords[2][0]+1), round(self.currentCoords[2][1]+float(self.Gradient))]:
            if [self.currentCoords[2][0]+val, self.currentCoords[2][1]+(val*float(self.Gradient))] < self.endPoint:
                for pair in self.currentCoords:
                    pair[0] += val
                    pair[1] += val * float(self.Gradient)
                return False
            else:
                return True
        else:
            return True

    def CalcVals(self):
        self.reactionForce = abs(self.weight * cos(radians(self.Angle)))
        self.friction = self.frictionConst * self.reactionForce

        self.acceleration = self.getAcceleration()
        self.distance = self.getDistance(self.slopeLine)

        if self.acceleration != 0:
            self.time = sqrt((2 * self.distance) / self.acceleration)
        else:
            self.time = 0

        self.distances, self.velocities = self.calculateMovements()

        self.maxCount = len(self.distances) - 1

    def calcBoxCoords(self, paraSlope):
        angle = self.Angle
        vertDist = self.slopeLine.startPoint[1] - paraSlope.startPoint[1]
        
        perpDist = vertDist * cos(radians(angle))
        self.lineSeg = vertDist * sin(radians(angle))

        xAdj = perpDist * sin(radians(angle))
        yAdj = self.lineSeg * sin(radians(angle))

        xAdj2 = perpDist * cos(radians(angle))
        yAdj2 = perpDist * sin(radians(angle))

        p2x = self.slopeLine.startPoint[0]
        p2y = self.slopeLine.startPoint[1]
            
        p1 = [paraSlope.startPoint[0]+xAdj, paraSlope.startPoint[1]+yAdj]
        p2 = [p2x, p2y]
        p3 = [self.slopeLine.startPoint[0]+xAdj2, self.slopeLine.startPoint[1]+yAdj2]
        p4 = [p1[0]+xAdj2, p1[1]+yAdj2]
        self.currentCoords = [p1, p2, p3, p4]

    def getAcceleration(self):
        forwardForce = self.weight * sin(radians(self.Angle))
        if self.frictionEnabled:
            acceleration = (forwardForce - self.friction) / self.mass
            if acceleration < 0:
                return 0
        else:
            acceleration = forwardForce / self.mass
        return acceleration

    def getDistance(self, slopeLine):
        vertDistTotal = (slopeLine.endPoint[1] - slopeLine.startPoint[1])/100
        horDistTotal = (slopeLine.endPoint[0] - slopeLine.startPoint[0])/100
        dist = sqrt((vertDistTotal)**2 + (horDistTotal)**2)
        return(dist - (self.lineSeg/100))

    def calculateMovements(self):
        dists = []
        velos = []
        iterCount = 0
        while self.distanceTotal <= self.distance and iterCount < 1000:
            s = (self.startV * self.timeDelay) + (0.5 * self.acceleration * (self.timeDelay**2))#m
            self.finalV = self.startV + (self.acceleration * self.timeDelay)#ms^-1
            self.startV = self.finalV

            velos.append(self.finalV)
            dists.append(s*100)
            self.distanceTotal += s

            iterCount += 1

        return(dists, velos)

    def moveLabels(self, distance):
        self.canvas.move(self.weightLine, distance, distance*float(self.Gradient))
        self.canvas.move(self.frictionLine, distance, distance*float(self.Gradient))
        self.canvas.move(self.reactionLine, distance, distance*float(self.Gradient))

    def createLabels(self):
        midW = ((self.currentCoords[2][0] + self.currentCoords[1][0])/2,
               (self.currentCoords[2][1] + self.currentCoords[1][1])/2)
        endPointW = (midW[0], midW[1]+50)
        self.weightLine = self.canvas.create_line(midW, endPointW, fill="red")

        midF = ((self.currentCoords[0][0] + self.currentCoords[1][0])/2,
               (self.currentCoords[0][1] + self.currentCoords[1][1])/2)
        endPointF = (-25, calcLineYCoord(self.Gradient, -25, midF[0], midF[1]))
        self.frictionLine = self.canvas.create_line(midF, endPointF, fill="blue")

        midR = ((self.currentCoords[0][0] + self.currentCoords[3][0])/2,
                (self.currentCoords[0][1] + self.currentCoords[3][1])/2)
        endPointR = (midR[0]+(50*self.Gradient), calcLineYCoord(-(1/self.Gradient),
                                                midR[0]+(50*self.Gradient), midR[0],midR[1]))
        self.reactionLine = self.canvas.create_line(midR, endPointR, fill="green")

    def eraseLabels(self):
        self.canvas.delete(self.weightLine)
        self.canvas.delete(self.frictionLine)
        self.canvas.delete(self.reactionLine)
    
    def StartMove(self, boxes, velLabel):
        self.DrawMe()

        self.createLabels()
        
        for count, distance in enumerate(self.distances, 0):
            if self.UpdateCoords(distance):
                break
            if self.buttonState.get():
                while self.buttonState.get():
                    time.sleep(0.1)
                    self.canvas.update()
            time.sleep(self.timeDelay + (self.sliderVal()/10))
            self.canvas.move(boxes[self.ident], distance, distance*float(self.Gradient))
            self.moveLabels(distance)
            self.canvas.update()
            try:
                velLabel["text"] = ("Velocity:", str(round(self.velocities[count], 3))+"ms^-1")
            except(TclError):
                pass

        
def calcStartY(slope, m):
    c = slope.endPoint[1] - (float(m) * slope.endPoint[0])
    slope.intercept = c
    yCoord = (float(m) * 5) + c
    StartCoords = [5, yCoord]
    slope.startPoint = StartCoords

def calcStartX(slope, m):
    c = slope.endPoint[1] - (float(m) * slope.endPoint[0])
    slope.intercept = c
    xCoord = (5 - c) / float(m)
    StartCoords = [xCoord, 5]
    slope.startPoint = StartCoords

def calcLineYCoord(m, x, x1, y1):
    y = m * (x-x1) + y1
    return y

def Start(master, SimMenu):
    if SimMenu != "" and SimMenu.state() == "normal":
        SimMenu.destroy()
    SimMenu = Toplevel(master)
    mainWindow = MainWindow(SimMenu)

if __name__ == "__main__":
    pass
