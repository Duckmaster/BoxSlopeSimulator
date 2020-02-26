from tkinter import *
from tkinter.ttk import *
import dbmanager
from threading import *
import special
import random
from os import listdir, remove
import pickle as p
import string
import hashfunc as h
import emailmod
import re
import datetime as dt
from math import ceil
try:
    import matplotlib.pyplot as plt
except:
    pass

QUESTION_DIR = "./Questions/"

## The main window that displays after the user presses the "Login" button
## on the main menu
class LoginWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Login Page")
        self.master.geometry("500x500+100+200")
        self.master.resizable(width=False, height=False)

        self.Username = StringVar()
        self.Password = StringVar()

        self.MainQuestionsWindowRoot = None

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(5, weight=1)

        Label(self.master, text="Username: ").grid(column=1, row=1)
        Label(self.master, text="Password: ").grid(column=1, row=2)
        self.errorLabel = Label(self.master, text="")
        self.errorLabel.grid(row=3, column=2)
        Entry(self.master, textvariable=self.Username).grid(column=2, row=1)
        Entry(self.master, textvariable=self.Password, show="*").grid(column=2, row=2)
        self.resetLabel = Label(self.master, text="Forgotten your password?")
        self.resetLabel.grid(row=4, column=3)
        Button(self.master, text="Submit", command=self.SubmitDetails).grid(row=4, column=2, pady=5)
        self.resetLabel.bind("<Button-1>", self.ResetPassword)

    def SubmitDetails(self):
        ## Retrieves the user's given login details and determines whether
        ## they are a valid user and if they are, their account type
        Username = self.Username.get()
        Password = self.Password.get()

        Found, Usertype = dbmanager.checkUserLogin(Username, Password)
        if not Found:
            self.errorLabel["text"] = "Username or password invalid"
            self.Password.set("")
        else:
            self.errorLabel["text"] = ""
            self.Username.set("")
            self.Password.set("")

            self.MainQuestionsWindowRoot = Toplevel(self.master)
            self.MainQuestionsWindowRoot.attributes("-topmost", True)
            if Usertype == "Student":
                t = Thread(target = lambda: special.RunCheck(self.master, self.MainQuestionsWindowRoot))
                t.start()
                self.MainQuestionsWin = QuestionsMainWindowStudent(self.MainQuestionsWindowRoot, Username)
            else:
                t = Thread(target = lambda: special.RunCheck(self.master, self.MainQuestionsWindowRoot))
                t.start()
                self.MainQuestionsWin = QuestionsMainWindowTutor(self.MainQuestionsWindowRoot, Username)

    def ResetPassword(self, event):
        ## Function for resetting the user's password
        chars = [chr(x) for x in range(65, 123) if chr(x).isalpha()]
        code = ""
        for x in range(7):
            code += chars[random.randint(0,len(chars)-1)]

        username = self.Username.get()
        found, userType = dbmanager.checkUserExists(username)

        if found and userType == "Student":
            userEmail = "{}@student.burnley.ac.uk".format(username)
        elif found and userType == "Tutor":
            usernamewithdot = "{}.{}".format(username[0],username[1:])
            userEmail = "{}@burnley.ac.uk".format(usernamewithdot)
        else:
            self.resetLabel["text"] = "Username not valid"
            self.master.after(3000, lambda: self.resetLabel.config(text="Forgotten your password?"))
            return False
        body = """You are receiving this email as a password reset has been requested for your account.
                  If you didn't request this reset, ignore this email. Otherwise, enter the following code into password reset form in the program.
                  Code: {}
                  This code will expire if you close the password reset form.""".format(code)
                    
        emailmod.send_email(userEmail, body)
        
        self.PasswordResetWindowRoot = Toplevel(self.master)
        self.PasswordResetWindowRoot.attributes("-topmost", True)
        PasswordResetWindow(self.PasswordResetWindowRoot, code, username)
        
class PasswordResetWindow:
    def __init__(self, master, code, studentID):
        self.master = master
        self.master.title("Password Reset")
        self.master.geometry("400x200+100+200")

        self.code = code
        self.studentID = studentID
        self.Code = StringVar()
        self.NewPass = StringVar()
        self.NewPassConfirm = StringVar()

        Label(self.master, text="An email has been sent to you, instructions are enclosed.").grid(row=0,
                                                                                                  column=0,
                                                                                                  columnspan=2,
                                                                                                  sticky="ew")
        Entry(self.master, textvariable=self.Code).grid(row=1, column=1, sticky="w")
        Label(self.master, text="Code:").grid(row=1, column=0, sticky="e")
        self.entryNewPass = Entry(self.master, textvariable=self.NewPass, state=DISABLED, show="*")
        self.entryNewPass.grid(row=2, column=1, sticky="w")
        Label(self.master, text="New password:").grid(row=2, column=0, sticky="e")
        self.entryNewPassConfirm = Entry(self.master, textvariable=self.NewPassConfirm, state=DISABLED, show="*")
        self.entryNewPassConfirm.grid(row=3, column=1, sticky="w")
        Label(self.master, text="Reenter new password:").grid(row=3, column=0, sticky="e")
        self.buttonSubmitCode = Button(self.master, text="Submit", command=self.checkCode)
        self.buttonSubmitCode.grid(row=4, column=1, columnspan=2)
        Button(self.master, text="Exit", command=self.master.destroy)

    def checkCode(self):
        ## Checks if the code the user inputs is the same as the one sent
        if self.code == self.Code.get():
            self.entryNewPass["state"] = NORMAL
            self.entryNewPassConfirm["state"] = NORMAL
            self.buttonSubmitCode["command"] = self.resetPass
        else:
            labelErrorTemp = Label(self.master, text="Incorrect code")
            labelErrorTemp.grid()
            self.master.after(3000, labelErrorTemp.destroy)

    ## Resets the user's password if both entries match
    def resetPass(self):
        if self.NewPass.get() == self.NewPassConfirm.get():
            salt = "".join([string.ascii_letters[random.randint(0, 51)] for i in range(8)])
            dbmanager.updateStudentPassword(h.Hash(self.NewPass.get()+salt), self.studentID, salt)
            labelSuccessTemp = Label(self.master, text="Password reset")
            labelSuccessTemp.grid()
            self.master.after(3000, self.master.destroy)
        else:
            labelErrorTemp = Label(self.master, text="Passwords do not match")
            labelErrorTemp.grid()
            self.master.after(3000, labelErrorTemp.destroy)            

## The main window where students are able to answer questions
class QuestionsMainWindowStudent:
    def __init__(self, master, studentID):
        self.master = master
        self.master.title("Questions")
        self.master.geometry("500x500+100+200")
        self.StudentID = studentID

        studentInfo = dbmanager.getStudentByID(self.StudentID)

        self.StudentClass = studentInfo[0]
        self.StudentForename = studentInfo[1]
        self.StudentSurname = studentInfo[2]
        self.StudentGrade = studentInfo[3]
        self.StudentGradeInt = studentInfo[4]
        self.StudentQuestions = studentInfo[5]

        self.master.grid_columnconfigure(2, weight=1)

        Label(self.master, text="Welcome, {0} {1}".format(self.StudentForename, self.StudentSurname)).grid()
        Button(self.master, text="Answer Questions", command=self.SelectQs).grid(row=1, column=1)
        Button(self.master, text="View answered questions", command=self.AnsweredQs).grid(row=2, column=1)
        Button(self.master, text="Log out", command=self.LogOut).grid(row=3,column=1)

    ## These open their corresponding window according to name

    def SelectQs(self):
        self.SelectQuestionsWindowRoot = Toplevel(self.master)
        self.SelectQuestionsWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.SelectQuestionsWindowRoot))
        t.start()
        self.SelectQuestionsWin = SelectQuestionsWindow(self.SelectQuestionsWindowRoot, self.StudentID)

    def AnsweredQs(self):
        self.AnsweredQuestionsWindowRoot = Toplevel(self.master)
        self.AnsweredQuestionsWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.AnsweredQuestionsWindowRoot))
        t.start()
        AnsweredQuestionsWindow(self.AnsweredQuestionsWindowRoot, self.StudentID)
        
    def LogOut(self):
        self.master.destroy()

## Window for a student to select the questions they want to answer
class SelectQuestionsWindow:
    def __init__(self, master, studentID):
        self.master = master
        self.master.title("Select Question(s)")
        self.master.geometry("500x500+100+200")

        self.studentID = studentID

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        self.qLabel = Label(self.master, text="Select question(s) to answer:")
        self.qLabel.grid(row=0, column=1)

        self.listbox = Listbox(self.master, selectmode=MULTIPLE)
        self.listbox.grid(row=1, column=1)
        self.listbox.bind("<<ListboxSelect>>", self.selectionChanged)

        self.buttonStart = Button(self.master, text="Go!",
                                  command=self.selectQuestions, state=DISABLED)
        self.buttonStart.grid(row=2, column=1)
        Button(self.master, text="Exit", command=self.Exit).grid(row=3,column=1)
    
        questionNames = self.getQuestions()
        for file in questionNames:
            self.listbox.insert(END, file)

    def getQuestions(self):
        ## Returns the list of files from the question directory
        files = listdir(QUESTION_DIR)
        return files

    def selectionChanged(self, event):
        ## Enables the start button when the user has selected a question
        if len(self.listbox.curselection()) > 0:
            self.buttonStart["state"] = NORMAL
        else:
            self.buttonStart["state"] = DISABLED

    def selectQuestions(self):
        ## Gets all of the questions the user has selected, adds them to a
        ## queue then opens the window for the user to answer the question(s)
        queueQuestions = Queue()
        selected = self.listbox.curselection()
        for item in selected:
            self.listbox.get(item)
            if type(self.listbox.get(item)) is tuple:
                queueQuestions.Enqueue(self.listbox.get(item)[0])
            else:
                queueQuestions.Enqueue(self.listbox.get(item)[:-9])

        self.AnswerQuestionsWindowRoot = Toplevel(self.master)
        self.AnswerQuestionsWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.AnswerQuestionsWindowRoot))
        t.start()
        AnswerQuestionsWindow(self.AnswerQuestionsWindowRoot, queueQuestions,
                              self.studentID)

    def Exit(self):
        self.master.destroy()

class AnsweredQuestionsWindow(SelectQuestionsWindow):
    def __init__(self, master, studentID):
        ## Inheriting from the parent class SelectQuestionsWindow as they are basically both the same
        SelectQuestionsWindow.__init__(self, master, studentID)
        self.master.title("Answered Question(s)")

        self.qLabel["text"] = "Currently answered questions and the most recent achieved grade:"
        self.buttonStart["text"] = "Retry"

    ## Overriding the parent method
    def getQuestions(self):
        data = dbmanager.getAnsweredQuestions(self.studentID)
        sep = []
        for q in data:
            sep.append(q[0:2])
        return sep

## Window where students answer the questions
class AnswerQuestionsWindow:
    def __init__(self, master, queueQuestions, studentID):
        self.master = master
        self.master.title("Questions")
        self.master.geometry("500x500+100+200")

        self.completedQuestions = Queue()

        self.studentID = studentID

        self.lastRow = 0
        self.noOfParts = 0
        self.parts = []

        self.buttonSubmit = Button(self.master, text="Submit", command=self.preSubmit)
        self.buttonSubmit.grid(row=0, column=1, sticky="ew")

        self.master.grid_columnconfigure(3, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        self.questionNames = list(queueQuestions.getQueue())
        self.questionAnswers = []
        self.queueQuestions = queueQuestions
        self.loadQuestion(self.queueQuestions.Dequeue())

    def loadQuestion(self, qName):
        ## Opens the question file determined by "qName"
        self.master.title("Questions - {}".format(qName))
        qName += ".question"
        path = QUESTION_DIR + qName
        reader = open(path, "rb")
        question = p.load(reader)

        partsNo = len(question)
        for part in question:
            mark = part[0]
            if part[4]:
                self.addPart(True, "", mark)
            else:
                unit = part[3]
                self.addPart(False, unit, mark)

            if part[4]:
                self.questionAnswers.append((part[0], part[2], part[3]))
            else:
                self.questionAnswers.append((part[0], part[2]))

        for x in range(partsNo):
            self.parts[x][0]["text"] = question[x][1]

    def addPart(self, reqUnit, unit, mark):
        ## Dynamically creates the entries, labels etc required for the form
        ## for the user to answer the question
        ## This function adds a single part to the window
        Answer = DoubleVar()

        lr = self.lastRow

        labelQuestion = Label(self.master, text="placeholder")
        labelQuestion.grid(row=lr+1, column=1, columnspan=3, sticky="ew")

        entryAnswer = Entry(self.master, textvariable=Answer)
        entryAnswer.grid(row=lr+2, column=2, sticky="e")

        labelMark = Label(self.master, text="({})".format(mark))
        labelMark.grid(row=lr+2, column=4)

        if reqUnit:
            Unit = StringVar()
            entryUnit = Entry(self.master, textvariable=Unit, width=5)
            entryUnit.grid(row=lr+2, column=3)
        else:
            labelUnit = Label(self.master, text=unit)
            labelUnit.grid(row=lr+2, column=3, sticky="w")

        self.lastRow = self.master.grid_size()[1]

        self.buttonSubmit.grid(row=self.lastRow+1)

        if reqUnit:
            widgets = [labelQuestion, labelMark, (entryAnswer, Answer), (entryUnit, Unit), reqUnit]
        else:
            widgets = [labelQuestion, labelMark, labelUnit, (entryAnswer, Answer), reqUnit]
        self.parts.append(widgets)
        self.noOfParts += 1

    def resetParts(self):
        ## Removes all parts from the window
        for part in self.parts:
            for widget in part[:-1]:
                if type(widget) == tuple:
                    widget[0].destroy()
                else:
                    widget.destroy()
        self.parts = []

    def preSubmit(self):
        ## Validation for the answer entry
        if not self.submitQuestion():
            red_style = Style()
            red_style.configure("Red.TLabel", foreground="red")
            errorLabel = Label(self.master, text="Your answer should be a number.", style="Red.TLabel")
            errorLabel.grid()
            self.master.after(3000, lambda: errorLabel.destroy())
                
    def submitQuestion(self):
        ## Stores the student's answers and resets the window.
        ## Displays the next question, if there is one, otherwise marks the
        ## student's answers.
        for part in self.parts:
            studentAnswers = []
            try:
                if part[4]:
                    studentAnswers.append(part[2][1].get())
                    studentAnswers.append(part[3][1].get())
                else:
                    studentAnswers.append(part[3][1].get())
            except:
                return False
            self.completedQuestions.Enqueue(studentAnswers)
            
        self.resetParts()
        if len(self.queueQuestions.getQueue()) > 0:
            self.loadQuestion(self.queueQuestions.Dequeue())
        else:
            self.markQuestions()
        return True

    def markQuestions(self):
        ## Marks the student's answers; if unit is being assessed, it is worth
        ## 1 mark, and the rest for the answer. Otherwise, all marks go for the
        ## answer.
        ## The results are then displayed and added to the database.
        marks = []
        for x in range(len(self.questionAnswers)):
            studentAnswers = self.completedQuestions.Dequeue()
            tempMark = 0
            if len(self.questionAnswers[x]) == 2:
                if "-" in self.questionAnswers[x][1]:
                    boundaries = self.questionAnswers[x][1].split("-")
                    if studentAnswers[0] >= float(boundaries[0]) and studentAnswers[0] <= float(boundaries[1]):
                        tempMark += self.questionAnswers[x][0]
                    else:
                        tempMark += 0
                else:
                    if studentAnswers[0] == float(self.questionAnswers[x][1]):
                        tempMark += self.questionAnswers[x][0]
                    else:
                        tempMark += 0
            else:
                if "-" in self.questionAnswers[x][1]:
                    boundaries = self.questionAnswers[x][1].split("-")
                    if ( studentAnswers[0] >= float(boundaries[0]) and studentAnswers[0] <= float(boundaries[1]) ) and studentAnswers[1] == self.questionAnswers[x][2]:
                        tempMark += self.questionAnswers[x][0]
                    elif studentAnswers[0] >= float(boundaries[0]) and studentAnswers[0] <= float(boundaries[1]):
                        tempMark += (self.questionAnswers[x][0]-1)
                    elif studentAnswers[1] == self.questionAnswers[x][2]:
                        tempMark += 1
                else:
                    if studentAnswers[0] == float(self.questionAnswers[x][1]) and studentAnswers[1] == self.questionAnswers[x][2]:
                        tempMark += self.questionAnswers[x][0]
                    elif studentAnswers[0] == float(self.questionAnswers[x][1]):
                        tempMark += (self.questionAnswers[x][0]-1)
                    elif studentAnswers[1] == self.questionAnswers[x][2]:
                        tempMark += 1
            marks.append(tempMark)

        partNos = []
        for name in self.questionNames:
            fName = QUESTION_DIR+name+".question"
            reader = open(fName, "rb")
            question = p.load(reader)
            count = 0
            for part in question:
                count += 1
            partNos.append(count)
            reader.close()

        totals = [x[0] for x in self.questionAnswers]
        totalMark = sum(totals)
        
        self.updateResult(marks, partNos, totals, totalMark)
        self.displayResults(partNos, marks, totals, totalMark)

    def updateResult(self, marks, partNos, totals, totalMark):
        ## Updates the student's stats in the database
        dbmanager.updateStudentStats(self.studentID, self.questionNames, marks, totals, partNos)
        
    def displayResults(self, partNos, marks, totals, totalMark):
        ## Displays the student's results for each question
        self.buttonSubmit.destroy()
        self.master.title("Questions - Results")
        totalStudent = sum(marks)
        labels = []
        offset = 0
        
        for i in range(len(partNos)):
            labelQuestion = Label(self.master, text="Question {}:".format(i+1))
            labelQuestion.grid()
            labels.append(labelQuestion)
            alphaPos = 0
            for j in range(offset, partNos[i]+offset):
                labelMark = Label(self.master, text="{0}) Score: {1}/{2}".format(string.ascii_lowercase[alphaPos],
                                                                                 marks[j], totals[j]))
                labelMark.grid()
                labels.append(labelMark)
                alphaPos += 1
            offset += partNos[i]
            labelSep = Label(self.master, text="\n")
            labelSep.grid()
            labels.append(labelSep)

        percent = round(((totalStudent/totalMark)*100),2)
        labelTotal = Label(self.master, text="Total: {0}/{1} = {2}%".format(totalStudent, totalMark, percent))
        labelTotal.grid()

        Button(self.master, text="Finish", command=self.master.destroy).grid()

## Main window for the tutor; has all administrative functions
class QuestionsMainWindowTutor:
    def __init__(self, master, tutorID):
        self.master = master
        self.master.title("Questions")
        self.master.geometry("500x500+100+200")
        self.TutorID = tutorID

        tutorInfo = dbmanager.getTutorByID(self.TutorID)

        self.TutorForename = tutorInfo[0]
        self.TutorSurname = tutorInfo[1]

        Label(self.master, text="Welcome, {0} {1}".format(self.TutorForename, self.TutorSurname)).grid()
        Button(self.master, text="View Students", command=self.openViewStudentWindow).grid(row=1, column=1)
        Button(self.master, text="Add New Student", command=self.openAddStudentWindow).grid(row=2, column=1)
        Button(self.master, text="View Classes", command = self.openViewClassesWindow).grid(row=3, column=1)
        Button(self.master, text="Add/Edit/Remove Questions", command=self.openAERQuestionsWindow).grid(row=4, column=1)
        Button(self.master, text="View Tutors", command=self.openViewTutorWindow).grid(row=5, column=1)
        Button(self.master, text="Add New Tutor", command=self.openAddTutorWindow).grid(row=6, column=1)
        Button(self.master, text="Log out", command=self.logOut).grid(row=7, column=1)

    ## Each of these open their corresponding window according to name
    
    def openViewStudentWindow(self):
        self.ViewStudentWindowRoot = Toplevel(self.master)
        t = Thread(target = lambda: special.RunCheck(self.master, self.ViewStudentWindowRoot))
        t.start()
        ViewStudentWindow(self.ViewStudentWindowRoot)

    def openAddStudentWindow(self):
        self.AddStudentWindowRoot = Toplevel(self.master)
        self.AddStudentWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.AddStudentWindowRoot))
        t.start()
        AddStudentWindow(self.AddStudentWindowRoot)

    def openViewClassesWindow(self):
        self.ViewClassesWindowRoot = Toplevel(self.master)
        self.ViewClassesWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.ViewClassesWindowRoot))
        t.start()
        ViewClassesWindow(self.ViewClassesWindowRoot)

    def openAERQuestionsWindow(self):
        self.AERQuestionsWindowRoot = Toplevel(self.master)
        self.AERQuestionsWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.AERQuestionsWindowRoot))
        t.start()
        AERQuestionsWindow(self.AERQuestionsWindowRoot)

    def openViewTutorWindow(self):
        self.ViewTutorWindowRoot = Toplevel(self.master)
        self.ViewTutorWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.ViewTutorWindowRoot))
        t.start()
        ViewTutorWindow(self.ViewTutorWindowRoot)

    def openAddTutorWindow(self):
        self.AddTutorWindowRoot = Toplevel(self.master)
        self.AddTutorWindowRoot.attributes("-topmost", True)
        t = Thread(target = lambda: special.RunCheck(self.master, self.AddTutorWindowRoot))
        t.start()
        AddTutorWindow(self.AddTutorWindowRoot)

    def logOut(self):
        self.master.destroy()

## Window that allows the tutor to search for a student and view their
## information
        
class ViewStudentWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Select Student")
        self.master.geometry("500x500+100+200")

        self.SurnameEntered = StringVar()
        self.NameSelected = StringVar()
        self.StudentID = StringVar()

        Label(self.master, text="Surname: ").grid(sticky="e")
        self.surnameEntry = Entry(self.master, textvariable=self.SurnameEntered)
        self.surnameEntry.grid(row=0,column=1)
        self.namesCombo = Combobox(self.master, textvariable=self.NameSelected)

        self.master.grid_rowconfigure(1, minsize=10)

        self.namesCombo.grid(row=2, column=1)
        self.labelID = Label(self.master, text="ID No.: ")
        self.labelID.grid(row=2, column=2)
        self.idEntry = Entry(self.master, textvariable=self.StudentID, state=DISABLED).grid(row=2, column=3)

        Separator(self.master, orient=HORIZONTAL).grid(row=3, columnspan=4, sticky="ew")

        self.Forename = StringVar()
        self.Surname = StringVar()
        self.Class = StringVar()
        self.Password = StringVar()

        self.labelForename = Label(self.master, text="Forename: ")
        self.labelSurname = Label(self.master, text="Surname: ")
        self.labelClass = Label(self.master, text="Class: ")
        self.labelPassword = Label(self.master, text="Password: ")

        self.entryForename = Entry(self.master, textvariable=self.Forename, state=DISABLED)
        self.entrySurname = Entry(self.master, textvariable=self.Surname, state=DISABLED)
        self.entryClass = Entry(self.master, textvariable=self.Class, state=DISABLED)
        self.entryPassword = Entry(self.master, textvariable=self.Password, state=DISABLED)

        self.buttonView = Button(self.master, text="View Student Data", command=lambda:self.openStudentDataWindow((self.NameSelected.get(), self.StudentID.get())))
        self.buttonEdit = Button(self.master, text="Edit Student", command=self.editStudent)
        self.buttonDelete = Button(self.master, text="Delete Student", command=self.deleteStudent)
        self.buttonExit = Button(self.master, text="Exit", command=self.Exit)

        self.labelError = Label(self.master, text="")

        self.surnameEntry.bind("<KeyRelease>", self.entryChanged)
        self.namesCombo.bind("<<ComboboxSelected>>", self.comboSelected)

    ## Detects when the contents of the search box have changed and updates
    ## the drop down box according to the new content
    def entryChanged(self, event):
        self.namesCombo["values"] = ("")
        surname = self.SurnameEntered.get()
        students = dbmanager.getStudentsBySurname(surname)
        studentNames = []
        for student in students:
            studentName = student[2], student[3]
            studentNames.append(studentName)
        if len(studentNames) == 0:
            studentNames.append("")
        self.namesCombo["values"] = studentNames
        self.namesCombo.current(0)

    ## Displays the information relating to the student that has been selected
    def comboSelected(self, event):
        selectedName = self.NameSelected.get()
        studentInfo = dbmanager.getStudentsBySurname(selectedName.split(" ")[1])[0]

        self.studentPass = studentInfo[6]
        self.studentSalt = studentInfo[7]
        
        self.StudentID.set(studentInfo[0])

        self.labelForename.grid(row=4)
        self.labelSurname.grid(row=4, column=2)
        self.master.grid_rowconfigure(5, minsize=10)
        self.labelClass.grid(row=6)
        self.labelPassword.grid(row=6, column=2)

        self.entryForename.grid(row=4, column=1)
        self.entrySurname.grid(row=4, column=3)
        self.entryClass.grid(row=6, column=1)
        self.entryPassword.grid(row=6, column=3)

        self.master.grid_rowconfigure(7, minsize=10)

        self.buttonView.grid(column=1, row=8)
        self.buttonEdit.grid(column=2, row=8)

        self.buttonDelete.grid(column=3, row=8)
        self.buttonExit.grid(column=2, row=9)

        self.labelError.grid(column=2, row=10, columnspan=3, sticky="EW")

        self.Forename.set(studentInfo[2])
        self.Surname.set(studentInfo[3])
        self.Class.set(studentInfo[1])
        self.Password.set("**********")

    def openStudentDataWindow(self, studentInfo):
        self.studentDataWindowRoot = Toplevel(self.master)
        StudentDataWindow(self.studentDataWindowRoot, studentInfo)

    ## Changes the window to allow for editing
    def editStudent(self):
        self.entryForename["state"] = NORMAL
        self.entrySurname["state"] = NORMAL
        self.entryClass["state"] = NORMAL
        self.entryPassword["state"] = NORMAL

        self.buttonEdit["command"] = self.commitEditStudent
        self.buttonEdit["text"] = "Submit"

    def deleteStudent(self):
        self.buttonDelete["text"] = "Confirm?"
        self.buttonDelete["command"] = self.confirmDeleteStudent

    ## Once user has confirmed deletion of student, student is deleted from
    ## the database
    def confirmDeleteStudent(self):
        dbmanager.deleteStudent(self.StudentID.get())
        self.buttonDelete["text"] = "Delete Student"
        self.buttonDelete["command"] = self.deleteStudent

        self.Forename.set("")
        self.Surname.set("")
        self.Class.set("")
        self.Password.set("")
        self.StudentID.set("")

        self.entryChanged("")

    ## Updates the student's information in the database once the tutor has
    ## finished editing
    ## Included validation for the group entry
    def commitEditStudent(self):
        forename = self.Forename.get()
        surname = self.Surname.get()
        group = self.Class.get()
        password = self.Password.get()

        if password == "**********":
            digest = self.studentPass
            salt = self.studentSalt
        else:
            self.Password.set("**********")

            salt = "".join([random.choice(string.ascii_letters) for x in range(8)])

            toHash = password+salt
            digest = h.Hash(toHash)

        classes = [x[0] for x in dbmanager.getClasses()]
        if group in classes:
            oldClass = dbmanager.getStudentByID(self.StudentID.get())[0]
            dbmanager.updateStudent(self.StudentID.get(), (forename, surname, group, digest, salt))
            dbmanager.updateClassAverage(oldClass)
            dbmanager.updateClassAverage(group)
        else:
            self.labelError["text"] = "Invalid group"
            self.master.after(3000, lambda: self.labelError.config(text=""))
            return False

        self.entryForename["state"] = DISABLED
        self.entrySurname["state"] = DISABLED
        self.entryClass["state"] = DISABLED
        self.entryPassword["state"] = DISABLED

        self.buttonEdit["command"] = self.editStudent
        self.buttonEdit["text"] = "Edit Student"

    def Exit(self):
        self.master.destroy()

## Window that displays all the question data about the student
class StudentDataWindow:
    def __init__(self, master, studentInfo):
        self.master = master

        self.studentName = studentInfo[0]
        self.studentID = studentInfo[1]

        title = "{}'s Data".format(self.studentName)     
        self.master.title(title)
        self.master.geometry("620x350+100+200")

        self.AverageGrade = StringVar()
        self.QuestionsCompleted = StringVar()

        Label(self.master, text="Completed Questions: ").grid()
        self.treeData = Treeview(self.master, columns=("dateCompleted", "gradeAchieved"))
        self.treeData.heading("#0", text="Question Name")
        self.treeData.column("#0", width=150)
        self.treeData.heading("dateCompleted", text="Date Completed")
        self.treeData.column("dateCompleted", width=150)
        self.treeData.heading("gradeAchieved", text="Grade Achieved")
        self.treeData.column("gradeAchieved", width=150)
        self.treeData.grid(row=1, sticky="ew", columnspan=5)

        self.master.grid_rowconfigure(2, minsize=10)
        Label(self.master, text="Average Grade: ").grid(row=3)
        Label(self.master, text="No. of completed questions").grid(row=3, column=4)

        Entry(self.master, textvariable=self.AverageGrade, state=DISABLED).grid(row=3, column=1)
        Entry(self.master, textvariable=self.QuestionsCompleted, state=DISABLED).grid(row=3, column=5)

        Button(self.master, text="Back", command=self.Back).grid(row=4, column=3)
        Button(self.master, text="Display graph", command=self.generateStudentGraph).grid(row=5, column=3)
    
        self.populateFields()

    def Back(self):
        self.master.destroy()

    def populateFields(self):
        studentPersonal, studentQuestions = dbmanager.getStudentDetails(self.studentID)

        self.AverageGrade.set(studentPersonal[3])
        self.QuestionsCompleted.set(studentPersonal[4])
        
        for question in studentQuestions:
            self.treeData.insert("", END, text=question[5],
                                 values=(question[0], question[1]))

    ## Calculates the student's average grade per week since the first question
    ## they answered and displays it in a graph
    def generateStudentGraph(self):
        currentDate = dt.datetime.now()
        firstDateStr = dbmanager.getFirstDateQuestionAnswered(self.studentID)
        firstDateObj = dt.datetime.strptime(firstDateStr, "%Y/%m/%d %H:%M:%S")
        
        times = ceil(((currentDate - firstDateObj).days)/7)
        boundaries = [firstDateObj]
        
        for y in (firstDateObj + dt.timedelta(days=x*7) for x in range(1, times+1)):
            boundaries.append(y)

        gradesFull = []
        boundariesStr = []
        for i in range(len(boundaries)-1):
            startObj = boundaries[i].replace(hour=0, minute=0, second=0)
            
            endObj = boundaries[i+1]

            startStr = dt.datetime.strftime(startObj, "%Y/%m/%d %H:%M:%S")
            endStr = dt.datetime.strftime(endObj, "%Y/%m/%d %H:%M:%S")

            boundariesStr.append(startStr.split(" ")[0])
            if i == len(boundaries)-1:
                boundariesStr.append(endStr.split(" ")[0])

            grades = dbmanager.getGradesInDateRange(startStr, endStr, self.studentID)
            gradesFull.append(grades)
        weeklyAvgGrades = []
        weeklyGradeInts = []
        grades = ['U', 'E', 'D', 'C', 'B', 'A', 'A*']
        for week in gradesFull:
            gradeIntTotal = 0
            for grade in week:
                gradeNT = grade[0]
                gradeInt = grades.index(gradeNT)
                gradeIntTotal += gradeInt
            if len(week):
                gradeIntTotal /= len(week)
            weeklyAvgGrades.append(grades[round(gradeIntTotal)])
            weeklyGradeInts.append(round(gradeIntTotal))

        plt.figure(figsize=(times*1.5,5))
        plt.bar(boundariesStr, weeklyGradeInts)
        plt.yticks([0,1,2,3,4,5,6],grades)
        plt.xlabel("Date")
        plt.ylabel("Grade")
        plt.show()

## Window for adding a new student
class AddStudentWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Add New Student")
        self.master.geometry("500x500+100+200")

        self.stackStudents = Stack()
        self.stackTemp = Stack()

        self.Forename = StringVar()
        self.Surname = StringVar()
        self.StudentID = StringVar()
        self.Class = StringVar()

        self.prevIndex = 0

        Label(self.master, text="Forename: ").grid()
        Label(self.master, text="Surname: ").grid(row=0,column=3, sticky="e")
        self.master.grid_rowconfigure(1, minsize=10)
        self.labelStudentID = Label(self.master, text="Student ID: ")
        self.labelStudentID.grid(row=2)
        self.labelClass = Label(self.master, text="Class: ")
        self.labelClass.grid(column=3, row=2)

        Entry(self.master, textvariable=self.Forename).grid(row=0, column=1)
        Entry(self.master, textvariable=self.Surname).grid(row=0,column=4)
        Entry(self.master, textvariable=self.StudentID).grid(row=2, column=1)
        self.comboClass = Combobox(self.master, textvariable=self.Class,
                                   values=[x[0] for x in dbmanager.getClasses()])
        self.comboClass.grid(row=2, column=4)
        self.comboClass.current(0)

        self.master.grid_rowconfigure(3, weight=1)

        self.listStudents = Listbox(self.master)
        self.listStudents.grid(column=4, row=4)

        self.listStudents.bind("<<ListboxSelect>>", self.selectionChanged)

        self.buttonEdit = Button(self.master, text="Submit Edit", command=self.submitEdit)
        self.buttonEdit.grid(column=4, row=5)

        self.master.grid_rowconfigure(6, weight=1)
        self.master.grid_columnconfigure(3, minsize=5)

        Button(self.master, text="Submit", command=self.Submit).grid(column=2, row=7)
        self.buttonAddNew = Button(self.master, text="Add New", command=self.addNew)
        self.buttonAddNew.grid(column=3, row=7)

        self.labelError = Label(self.master, text="")
        self.labelError.grid(column=0, row=7, columnspan=2)

    ## If the given information is valid, adds the student(s) to the database
    def Submit(self):
        if self.checkInputs():
            self.addNew()
            students = self.stackStudents.getStack()
            dbmanager.addMultipleStudents(students)
            self.Exit()

    ## Checks if the given information is valid, then resets for a new entry  
    def addNew(self):
        Forename = self.Forename.get()
        Surname = self.Surname.get()
        StudentID = self.StudentID.get()
        Class = self.Class.get()

        if self.checkInputs():
            salt = "".join([string.ascii_letters[random.randint(0, 51)] for i in range(8)])
            self.stackStudents.Push((StudentID, Class,
                                        Forename, Surname, h.Hash("password"+salt), salt))

            self.Forename.set("")
            self.Surname.set("")
            self.StudentID.set("")

            self.comboClass.current(0)
            self.updateListbox()

    def updateListbox(self):
        self.listStudents.delete(0, END)
        studentList = self.stackStudents.getStack()
        for student in studentList:
            self.listStudents.insert(END, (student[2], student[3]))

    ## Loads the selected student's data from the listbox into the entries
    ## and disables the listbox
    def selectionChanged(self, event):
        self.listStudents["state"] = DISABLED
        
        curIndex = self.listStudents.curselection()[0]
        curItem = self.listStudents.get(curIndex)

        stackContents = self.stackStudents.getStack()

        difference = curIndex - self.prevIndex
        eDifference = (len(stackContents)-1) - difference
        if eDifference > 0:
            for x in range(eDifference):
                item = self.stackStudents.Pop()
                self.stackTemp.Push(item)
        info = self.stackStudents.Pop()

        studentID, Class, forename, surname, password, salt = info

        self.Forename.set(forename)
        self.Surname.set(surname)
        self.Class.set(Class)
        self.StudentID.set(studentID)

    def submitEdit(self):
        self.addNew()
        if len(self.stackTemp.getStack()) > 0:
            for x in range(len(self.stackTemp.getStack())):
                self.stackStudents.Push(self.stackTemp.Pop())

        self.listStudents["state"] = NORMAL
        self.updateListbox()

    ## Validation
    def checkInputs(self):
        self.labelError["text"] = ""
        error = ""
        if self.Forename.get() == "":
            error = ("Forename", "be empty")
        elif self.Surname.get() == "":
            error = ("Surname", "be empty")
        elif self.StudentID.get() == "":
            error = ("Student ID", "be empty")
        elif dbmanager.getStudentByID(self.StudentID.get()) != None:
            error = ("Student ID", "already exist")
        ## Regular expression used here to check that the inputted student ID is in the correct
        ## format that the college uses
        elif re.fullmatch("10014[0-9]{4}", self.StudentID.get()) == None:
            error = ("Student ID", "have incorrect format")

        if error != "":
            self.labelError["text"] = "{} cannot {}.".format(error[0], error[1])
            self.master.after(3000, lambda: self.labelError.config(text=""))
            return False
        else:
            return True
        
    def Exit(self):
        self.master.destroy()

## Window for a tutor to select a class
class ViewClassesWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Select Class")
        self.master.geometry("500x500+100+200")

        self.Class = StringVar()
        self.Tutor = StringVar()
        self.Grade = StringVar()

        Label(self.master, text="Class: ").grid()
        self.comboClass = Combobox(self.master, textvariable=self.Class)
        self.comboClass.grid(row=0, column=1)
        self.comboClass.set("")
        self.comboClass.bind("<<ComboboxSelected>>", self.comboSelected)

        self.master.grid_columnconfigure(2, weight=1)

        Separator(self.master).grid(row=1, sticky="ew", columnspan=3)

        self.labelTree = Label(self.master, text="Students in this group: ")
        self.labelTutor = Label(self.master, text="Tutor: ")
        self.labelGrade = Label(self.master, text="Group\n average grade: ")

        self.treeStudents = Treeview(self.master, columns=("averageGrade"))
        self.treeStudents.heading("#0", text="Student Name")
        self.treeStudents.column("#0", width=125)
        self.treeStudents.heading("averageGrade", text="Average Grade")
        self.treeStudents.column("averageGrade", width=125)

        self.comboTutor = Combobox(self.master, textvariable=self.Tutor,
                                state=DISABLED, width=15)
        self.buttonEdit = Button(self.master, text="Edit", command=self.editClass)
        self.entryGrade = Entry(self.master, textvariable=self.Grade,
                                state=DISABLED, width=2)

        self.buttonBack = Button(self.master, text="Back", command=self.Exit)

        self.populateCombos()

    ## Fills the combobox with all classes stored in the database
    def populateCombos(self):
        classes = [item[0] for item in dbmanager.getClasses()]
        self.comboClass["values"] = classes
        self.comboClass.current(0)

        tutors = [item[1]+" "+item[2] for item in dbmanager.getTutors()]
        self.comboTutor["values"] = tutors

    ## Displays the information about the class when one has been selected
    def comboSelected(self, event):
        self.treeStudents.delete(*self.treeStudents.get_children())
        
        classInfo, students = dbmanager.getClass(self.Class.get())

        self.Tutor.set((classInfo[3], classInfo[4]))
        self.Grade.set(classInfo[2])

        for student in students:
            self.treeStudents.insert("", END, text=(student[1],student[0]),
                                 values=(student[2]))

        self.labelTree.grid(column=0, row=2)
        self.treeStudents.grid(column=0, row=3, columnspan=2, rowspan=3,
                               sticky="w")
        self.labelTutor.grid(column=2, row=3, sticky="e")
        self.comboTutor.grid(column=3, row=3, sticky="w")
        self.buttonEdit.grid(column=3, row=4, sticky="nw")
        self.labelGrade.grid(column=2, row=5, sticky="e")
        self.entryGrade.grid(column=3, row=5, sticky="w")
        self.buttonBack.grid(column=1, row=6, sticky="e")

        self.master.grid_columnconfigure(4, minsize=20)

    ## Allows for editing the tutor of a class
    def editClass(self):
        self.comboTutor["state"] = NORMAL
        self.buttonEdit["text"] = "Submit"
        self.buttonEdit["command"] = self.submitEditClass

    ## Submits the changes to the database and resets the window
    def submitEditClass(self):
        tutorID = dbmanager.getTutorsBySurname(self.Tutor.get().split(" ")[1])[0][0]
        dbmanager.updateClass(self.Class.get(), tutorID)
        self.buttonEdit["text"] = "Edit"
        self.buttonEdit["command"] = self.editClass
        self.comboTutor["state"] = DISABLED

    def Exit(self):
        self.master.destroy()

## Window for adding/editing/removing a question
class AERQuestionsWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Add/Edit/Remove Question(s)")
        self.master.geometry("550x550+100+100")

        self.QuestionName = StringVar()

        self.lastRow = 0
        self.noOfParts = 0
        self.parts = []

        Label(self.master, text="Question name: ").grid()
        self.master.grid_rowconfigure(1, minsize=10)

        Entry(self.master, textvariable=self.QuestionName).grid(row=0, column=1)

        self.separator = Separator(self.master, orient=VERTICAL)
        self.separator.grid(column=4, row=0, rowspan=6, sticky="ns")

        bottomRow = self.master.grid_size()[1]
        self.buttonSubmit = Button(self.master, text="Submit", command=lambda:self.submitQuestion(""))
        self.buttonAdd = Button(self.master, text="Add Part", command=self.addPart)
        self.buttonRemove = Button(self.master, text="Remove part",command=self.removePart)

        
        Label(self.master, text="Current questions: ").grid(row=0, column=5)
        self.listQuestions = Listbox(self.master)
        self.listQuestions.grid(row=1, column=5, rowspan=6)
        self.buttonDeleteQuestion = Button(self.master, text="Delete", command=self.deleteQuestion)
        self.buttonDeleteQuestion.grid(row=10, column=5)
        self.buttonSubmitEdit = Button(self.master, text="Submit edit", command=self.submitEdit,
                                       state=DISABLED)
        self.buttonSubmitEdit.grid(row=11, column=5)
        self.listQuestions.bind("<Double-Button-1>", self.selectionChanged)

        self.addPart()
        self.buttonRemove["state"] = DISABLED
        self.updateListbox()
        
    def submitQuestion(self, mode):
        ## Retrieves all values from entries and pickles them to a file in
        ## a series of arrays that can later be retrieved
        ##
        ## Includes validation for the unit entry; if the checkbox is ticked, a unit
        ## is required to be inputted or otherwise an error label is created
        toWrite = []
        QuestionName = self.QuestionName.get()

        valid = True

        fileName = QuestionName + ".question"
        maxMark = 0

        red_style = Style()
        red_style.configure("Red.Label", foreground="red")

        for part in self.parts:
            error = ""
            if part[6][1].get() == "" or part[7][1].get() == "":
                valid = False
                error = "1 or more required fields are missing."
            elif not self.isValidNum(part[6][1].get()):
                valid = False
                error = "The answer should be a number."
                
            maxMark += int(part[4][1].get())

        if not valid:
            labelError = Label(self.master, text=error, style="Red.Label")
            labelError.grid(row=self.lastRow, column=2, columnspan=3)
            self.master.after(2000, lambda: labelError.destroy())
        
        for part in self.parts:
            temp = []
            for widget in part[4:]:
                temp.append(widget[1].get())
            toWrite.append(temp)

        if mode == "" and fileName in listdir(QUESTION_DIR):
            valid = False
            labelError = Label(self.master, text="File name already exists.", style="Red.Label")
            labelError.grid(row=self.lastRow, column=2, columnspan=3)
            self.master.after(2000, lambda: labelError.destroy())
        
        if valid:
            fileWriter = open(("./Questions/"+fileName), "wb")
            p.dump(toWrite, fileWriter)
            self.updateListbox()
            fileWriter.close()


            ## Resets the input form back to a default state (1 part, empty) ready
            ## for another question to be inputted
            for i in range(0,len(self.parts)-1):
                self.removePart()

            self.QuestionName.set("")
            for part in self.parts:
                for widget in part[4:]:
                    if type(widget[1]) == StringVar:
                        widget[1].set("")
                    else:
                        widget[1].set(0)

            exists = False
            for question in dbmanager.getQuestions():
                if question[2] == QuestionName:
                    exists = True

            if not exists:
                dbmanager.addQuestion(maxMark, QuestionName)
            else:
                dbmanager.updateQuestion(maxMark, QuestionName)

        return valid

    def addPart(self):
        ## Dynamic creation of TKinter entry boxes and their labels, storing these and the
        ## associated TKinter vars in tuples in arrays which then are appending to the class
        ## attribute containing all parts
        lr = self.lastRow

        MaxMark = IntVar()
        QuestionText = StringVar()
        Answer = StringVar()
        Unit = StringVar()
        ReqUnit = BooleanVar()
        
        labelQT = Label(self.master, text="Question text: ")
        labelQT.grid(row=lr+3)
        labelA = Label(self.master, text="Answer: ")
        labelA.grid(row=lr+4)
        labelMark = Label(self.master, text="Max mark: ")
        labelMark.grid(row=lr+2)
        labelUnit = Label(self.master, text="Unit: ")
        labelUnit.grid(row=lr+4, column=2, sticky="E")

        entryMark = Entry(self.master, textvariable=MaxMark)
        entryMark.grid(row=lr+2, column=1)
        entryQT = Entry(self.master, textvariable=QuestionText)
        entryQT.grid(row=lr+3, column=1)
        entryA = Entry(self.master, textvariable=Answer)
        entryA.grid(row=lr+4, column=1)
        entryUnit = Entry(self.master, textvariable=Unit)
        entryUnit.grid(row=lr+4, column=3)

        checkUnit = Checkbutton(self.master, text="Require unit?", variable=ReqUnit,
                                command=lambda: self.checkToggled(ReqUnit, Unit))

        checkUnit.grid(row=lr+5, column=3)

        self.lastRow = self.master.grid_size()[1]

        self.buttonSubmit.grid(column=1, row=self.lastRow+1)
        self.buttonAdd.grid(column=2, row=self.lastRow+1)
        self.buttonRemove.grid(column=3, row=self.lastRow+1)

        self.separator.grid(column=4, row=0, rowspan=self.lastRow, sticky="ns")

        widgets = [labelQT, labelA, labelMark, labelUnit,
                   (entryMark, MaxMark), (entryQT,QuestionText),
                   (entryA,Answer), (entryUnit,Unit), (checkUnit, ReqUnit)]

        self.parts.append(widgets)
        self.noOfParts += 1

        if len(self.parts) >= 5:
            self.buttonAdd["state"] = DISABLED
        if str(self.buttonRemove["state"]) == "disabled":
            self.buttonRemove["state"] = NORMAL

    def getQuestions(self):
        directory = "./Questions"
        questions = listdir(directory)
        return questions

    def updateListbox(self):
        self.listQuestions.delete(0, END)
        for file in self.getQuestions():
            self.listQuestions.insert(END, file)

    def checkToggled(self, ReqUnit, Unit):
        if not ReqUnit.get():
            Unit.set("")

    def deleteQuestion(self):
        q = self.listQuestions.get(ACTIVE)
        remove("./Questions/"+q)
        self.updateListbox()
        dbmanager.deleteQuestion(q[:-9])

    ## Removes a part section of the question from the window
    def removePart(self):
        widgets = self.parts[-1]
        for widget in widgets:
            if type(widget) == tuple: 
                widget[0].destroy()
            else:
                widget.destroy()
        self.parts.pop()

        if len(self.parts) == 1:
            self.buttonRemove["state"] = DISABLED

        if len(self.parts) <= 5:
            self.buttonAdd["state"] = NORMAL

        self.noOfParts -= 1

    ## Submits the edit to a question if it is valid, then restores the window
    def submitEdit(self):
        if self.submitQuestion("edit"):
            self.listQuestions["state"] = NORMAL
            self.buttonSubmit["state"] = NORMAL
            self.buttonSubmitEdit["state"] = DISABLED
            self.buttonDeleteQuestion["state"] = NORMAL

    ## Loads a question when one has been selected to edit from the listbox
    def selectionChanged(self, event):
        self.listQuestions["state"] = DISABLED
        self.buttonSubmit["state"] = DISABLED
        self.buttonSubmitEdit["state"] = NORMAL
        self.buttonDeleteQuestion["state"] = DISABLED
        
        selectedIndex = self.listQuestions.curselection()[0]
        filename = self.listQuestions.get(selectedIndex)
        fileReader = open("./Questions/"+filename, "rb")

        question = p.load(fileReader)
        self.QuestionName.set(filename[:-9])

        diff = len(question) - self.noOfParts

        if diff < 0:
            for x in range(abs(diff)):
                self.removePart()
        elif diff > 0:
            for x in range(diff):
                self.addPart()

        count = 0
        for part in self.parts:
            part[4][1].set(question[count][0])
            part[5][1].set(question[count][1])
            part[6][1].set(question[count][2])
            if question[count][4]:
                part[7][1].set(question[count][3])
                part[8][1].set(1)
                part[7][0]["state"] = NORMAL
            else:
                #part[7][0]["state"] = DISABLED
                part[7][1].set(question[count][3])
                part[8][1].set(0)
            count += 1

    def isValidNum(self,num):
        try:
            float(num)
            return True
        except:
            return False

## More inheritance has been used in the classes "ViewTutorWindow" and
## "AddTutorWindow" below as the code is very similar to the classes
## that perform these functions for students.
## See comments for the parent classes for comments relating to these

class ViewTutorWindow:
    def __init__(self, master):
        ViewStudentWindow.__init__(self, master)
        self.master = master
        self.master.title("Select Tutor")

        self.buttonEdit["text"] = "Edit"
        self.buttonDelete["text"] = "Delete"
        self.labelID["text"] = "ID:"
        
    def entryChanged(self, event):
        self.namesCombo["values"] = ("")
        surname = self.SurnameEntered.get()
        tutors = dbmanager.getTutorsBySurname(surname)
        tutorNames = []
        for tutor in tutors:
            tutorName = tutor[1], tutor[2]
            tutorNames.append(tutorName)
        if len(tutorNames) == 0:
            tutorNames.append("")
        self.namesCombo["values"] = tutorNames
        self.namesCombo.current(0)

    def comboSelected(self, event):
        selectedName = self.NameSelected.get()
        tutorInfo = dbmanager.getTutorsBySurname(selectedName.split(" ")[1])[0]

        self.tutorPass = tutorInfo[3]
        self.tutorSalt = tutorInfo[4]
        
        self.StudentID.set(tutorInfo[0])

        self.labelForename.grid(row=4)
        self.labelSurname.grid(row=4, column=2)
        self.master.grid_rowconfigure(5, minsize=10)
        self.labelPassword.grid(row=6, column=2)

        self.entryForename.grid(row=4, column=1)
        self.entrySurname.grid(row=4, column=3)
        self.entryPassword.grid(row=6, column=3)

        self.master.grid_rowconfigure(7, minsize=10)

        self.buttonEdit.grid(column=1, row=8)
        self.buttonDelete.grid(column=2, row=8)
        self.buttonExit.grid(column=3, row=8)

        self.labelError.grid(column=2, row=10, columnspan=3, sticky="EW")

        self.Forename.set(tutorInfo[1])
        self.Surname.set(tutorInfo[2])
        self.Password.set("**********")

        if tutorInfo[0] == "admin":
            self.buttonDelete["state"] = DISABLED
        else:
            self.buttonDelete["state"] = NORMAL

    def openStudentDataWindow(self, studentInfo):
        pass

    def editStudent(self):
        return ViewStudentWindow.editStudent(self)

    def deleteStudent(self):
        return ViewStudentWindow.deleteStudent(self)

    def confirmDeleteStudent(self):
        dbmanager.deleteTutor(self.StudentID.get())
        self.buttonDelete["text"] = "Delete"
        self.buttonDelete["command"] = self.deleteStudent

        tutors = dbmanager.getTutors()
        for Class in dbmanager.getClasses():
            if Class[1] == self.StudentID.get():
                dbmanager.updateClass(Class[0], tutors[0][0])

        self.Forename.set("")
        self.Surname.set("")
        self.Password.set("")
        self.StudentID.set("")

        self.entryChanged("")

        

    def commitEditStudent(self):
        forename = self.Forename.get()
        surname = self.Surname.get()
        password = self.Password.get()

        if password == "**********":
            digest = self.tutorPass
            salt = self.tutorSalt
        else:
            self.Password.set("**********")

            salt = "".join([random.choice(string.ascii_letters) for x in range(8)])

            toHash = password+salt
            digest = h.Hash(toHash)

        dbmanager.updateTutor(self.StudentID.get(), forename, surname, digest, salt)

        self.entryForename["state"] = DISABLED
        self.entrySurname["state"] = DISABLED
        self.entryClass["state"] = DISABLED
        self.entryPassword["state"] = DISABLED

        self.buttonEdit["command"] = self.editStudent
        self.buttonEdit["text"] = "Edit"

    def Exit(self):
        self.master.destroy()

class AddTutorWindow:
    def __init__(self, master):
        AddStudentWindow.__init__(self, master)
        self.master = master
        self.master.title("Add New Tutor")

        self.comboClass.grid_remove()
        self.labelClass.grid_remove()
        self.labelStudentID["text"] = "Tutor ID:"

        self.listStudents.grid_remove()
        self.buttonEdit.grid_remove()
        self.buttonAddNew.grid_remove()

    def Submit(self):
        if self.checkInputs():
            salt = "".join([string.ascii_letters[random.randint(0, 51)] for i in range(8)])
            dbmanager.addTutor(self.StudentID.get(), self.Forename.get(), self.Surname.get(),
                               h.Hash("password"+salt), salt)
            self.Exit()
            
    def addNew(self):
        pass

    def updateListbox(self):
        pass

    def selectionChanged(self, event):
        pass

    def submitEdit(self):
        pass

    def checkInputs(self):
        self.labelError["text"] = ""
        error = ""
        if self.Forename.get() == "":
            error = ("Forename", "be empty")
        elif self.Surname.get() == "":
            error = ("Surname", "be empty")
        elif self.StudentID.get() == "":
            error = ("Tutor ID", "be empty")
        elif dbmanager.getTutorByID(self.StudentID.get()) != None:
            error = ("Tutor ID", "already exist")
        ## Regular expression used here to check that the inputted student ID is in the correct
        ## format that the college uses
        elif re.fullmatch("[a-zA-Z]+(0-9)?", self.StudentID.get()) == None:
            error = ("Tutor ID", "have incorrect format")

        if error != "":
            self.labelError["text"] = "{} cannot {}.".format(error[0], error[1])
            self.master.after(3000, lambda: self.labelError.config(text=""))
            return False
        else:
            return True
        
    def Exit(self):
        self.master.destroy()

## Classes for queues and stacks

class Queue:
    def __init__(self):
        self._Head = 0
        self._Tail = 0
        self._Items = []

    def Peek(self):
        return self._Items[self._Head]

    def Enqueue(self, item):
        self._Items.insert(self._Tail+1, item)
        self._Tail += 1
        return True

    def Dequeue(self):
        popped = self._Items.pop(self._Head)
        return popped

    def getQueue(self):
        return self._Items

class Stack:
    def __init__(self):
        self._Head = 0
        self._Tail = 0
        self._Items = []

    def Peek(self):
        if len(self._Items) == 0:
            return False
        else:
            return self._Items[self._Tail-1]

    def Push(self, item):
        self._Items.append(item)
        self._Tail += 1
        return True

    def Pop(self):
        self._Tail -= 1
        return self._Items.pop()

    def getStack(self):
        return self._Items







