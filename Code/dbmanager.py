import sqlite3
import re
import hashfunc as h
import string
import datetime
import random

## Location of the database, will usually be in the shared drive
## but in case it cannot find it, it will revert to a local version
__DBLOC = "X:\George's DB\database.db"
try:
    sqlite3.connect(__DBLOC)
except:
    __DBLOC = "../Database/database.db"

################### Create the tables if they dont exist #######################
def __createTables():
    __createStudents()
    __createCompleted()
    __createQuestions()
    __createTutors()
    __createClasses()

def __createStudents():
    sql = """CREATE TABLE IF NOT EXISTS `Students` (
	`StudentID`	TEXT,
	`ClassID`	TEXT,
	`Forename`	TEXT,
	`Surname`	TEXT,
	`AverageGrade`	TEXT,
	`GradeInt`      INTEGER,
	`QuestionsCompleted`	INTEGER,
	`Pass`	TEXT,
	`Salt`	TEXT UNIQUE,
	PRIMARY KEY(`StudentID`));"""
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)
    

def __createCompleted():
    sql = """CREATE TABLE IF NOT EXISTS `Completed` (
	`StudentID`	INTEGER,
	`QuestionID`	INTEGER,
	`DateCompleted`	TEXT,
	`MarkAchieved`	INTEGER,
	`GradeAchieved`	INTEGER,
	PRIMARY KEY(`QuestionID`,`DateCompleted`,`StudentID`)
);"""
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)
    
def __createQuestions():
    sql = """CREATE TABLE IF NOT EXISTS `Questions` (
	`QuestionID`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`MaxMark`	INTEGER,
	`FileName`      STRING
);"""
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)

def __createTutors():
    sql = """CREATE TABLE IF NOT EXISTS `Tutors` (
	`TutorID`	TEXT,
	`Forename`	TEXT,
	`Surname`	TEXT,
	`Pass`	TEXT,
	`Salt`	TEXT UNIQUE,
	PRIMARY KEY(`TutorID`)
);"""
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)
    if "admin" not in [x[0] for x in getTutors()]:
        salt = "".join([string.ascii_letters[random.randint(0, 51)] for i in range(8)])
        addTutor("admin", "admin", "account", h.Hash("admin"+salt), salt)

def __createClasses():
    sql = """CREATE TABLE IF NOT EXISTS `Classes` (
	`ClassID`	TEXT,
	`TutorID`	TEXT,
	`ClassAverageGrade`	TEXT,
	PRIMARY KEY(`ClassID`)
);"""
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)

    __addClasses()

############################ Student functions ###################################

def checkStudentExists(value):
    ## Check whether a student with a certain ID exists within the database
    ## Returns True if they do, False if not
    with sqlite3.connect(__DBLOC) as db:
        sql = "SELECT StudentID FROM Students WHERE StudentID == ?"
        cursor = db.cursor()
        cursor.execute(sql, value)
        record = cursor.fetchone()
        if record != None:
            return True
        else:
            return False

def addStudent(values):
    ## Inserts new record in "Students" table
    ## Valid values include StudentID, ClassID, Forename, Surname, Pass, Salt
    if checkStudentExists((values[0],)):
        return False
    
    with sqlite3.connect(__DBLOC) as db:
        sql = "INSERT INTO Students VALUES(?,?,?,?,'U',0,0,?,?)"
        cursor = db.cursor()
        cursor.execute(sql, values)
        db.commit()
    return True

def addMultipleStudents(values):
    ## Inserts multiple new records into "Students" table
    ## Valid values same as "addStudent" but 2d tuple
    students = []
    for student in values:
        if not checkStudentExists((student[0],)):
            students.append(student)
        else:
            return False

    if students == []:
        return False
    
    with sqlite3.connect(__DBLOC) as db:
        sql = "INSERT INTO Students VALUES(?,?,?,?,'U',0,0,?,?)"
        cursor = db.cursor()
        cursor.executemany(sql, students)
        db.commit()
    return True

def getStudentsBySurname(name):
    sql = "SELECT StudentID, ClassID, Forename, Surname, AverageGrade, QuestionsCompleted, Pass, Salt"\
            " FROM Students"\
            " WHERE Surname like ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, ("%"+name+"%",))
    students = cursor.fetchall()
    return students

def getStudentsByGrade(grade):
    sql = "SELECT StudentID, ClassID, Forename, Surname, QuestionsCompleted"\
            " FROM Students"\
            " WHERE AverageGrade == ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (grade,))
    students = cursor.fetchall()
    return students

def getStudentsByQuestions(number):
    sql = "SELECT StudentID, ClassID, Forename, Surname, AverageGrade"\
            " FROM Students"\
            " WHERE QuestionsCompleted = ?"
    db = sqlite3.connect(__DBLOC)
    cursor=db.cursor()
    cursor.execute(sql, (number,))
    students = cursor.fetchall()
    return students

def getStudentByID(idno):
    sql = "SELECT ClassID, Forename, Surname, AverageGrade, GradeInt, QuestionsCompleted"\
          " FROM Students"\
          " WHERE StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (idno,))
    studentInfo = cursor.fetchone()
    return studentInfo

def getStudentsByClass(className):
    sql = "SELECT StudentID, Forename, Surname, AverageGrade, GradeInt, QuestionsCompleted"\
          " FROM Students"\
          " WHERE ClassID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (className,))
    students = cursor.fetchall()
    return students

def getStudents():
    ## Returns the data of all students within the database
    sql = "SELECT *"\
          " FROM Students"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, ())
    students = cursor.fetchall()
    return students

def updateStudent(studentID, values):
    ## Updates properties of a student with ID of studentID
    sql = "UPDATE Students"\
          " SET ClassID = ?, Forename = ?, Surname = ?, Pass = ?, Salt = ?"\
          " WHERE StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (values[2], values[0], values[1], values[3], values[4], studentID))
    db.commit()

def updateCompleted(studentID, fileName, mark, grade):
    ## Once a student has completed a question, a record is inserted into the
    ## 'Completed' table detailing the student's score, date completed etc
    sql = "SELECT QuestionID"\
          " FROM Questions"\
          " WHERE FileName = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (fileName,))
    questionID = cursor.fetchone()

    date = datetime.date.today().strftime("%Y/%m/%d")
    time = datetime.datetime.now().time().strftime("%H:%M:%S")
    dt = date + " " + time
    
    sql = "INSERT INTO Completed"\
          " Values(?, ?, ?, ?, ?)"
    cursor.execute(sql, (studentID, questionID[0], dt, mark, grade))
    db.commit()
    
# studentMarks is the total the student scored PER PART,
# totals is the total mark PER PART
def updateStudentStats(studentID, questionNames, studentMarks, totals, partNos):
    ## Updates the statistics (grade, total questions completed etc) of a student
    ## once they have completed 1 or multiple questions
    ## Average grades are calculated by converting the student's achieved grade into
    ## an integer (grade int) then adding this onto the students preexisting 'grade int'
    ## then dividing by the new total number of questions completed to give an average
    ## grade for the student
    sql = "SELECT AverageGrade, QuestionsCompleted, GradeInt"\
          " FROM Students"\
          " WHERE StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (studentID,))
    currentStats = cursor.fetchone()
    oldGradeInt = currentStats[2] * currentStats[1]
    grades = ['U', 'E', 'D', 'C', 'B', 'A', 'A*']

    marksPerQ = []
    studentMarksPerQ = []
    offset = 0
    
    for i in range(len(partNos)):
        mPQtemp = 0
        sMPQtemp = 0
        for j in range(offset, partNos[i]+offset):
            mPQtemp += totals[j]
            sMPQtemp += studentMarks[j]
        marksPerQ.append(mPQtemp)
        studentMarksPerQ.append(sMPQtemp)
        offset += partNos[i]

    for i in range(len(questionNames)):
        gradeInt = 0
        grade = ""
        
        studentPercent = round(studentMarksPerQ[i]/marksPerQ[i], 1) * 100
        boundaries = [range(0,40), range(40, 50), range(50, 60), range(60, 70),
                      range(70, 80), range(80, 90), range(90, 101)]
        for boundary in boundaries:
            if studentPercent in boundary:
                
                gradeInt = boundaries.index(boundary)
                grade = grades[gradeInt]
    
        oldGradeInt += gradeInt
        updateCompleted(studentID, questionNames[i], studentMarksPerQ[i], grade)

    newQuestionAmount = currentStats[1]+len(questionNames)
    gradeInt = oldGradeInt / newQuestionAmount

    newGrade = grades[round(gradeInt)]

    sql = "UPDATE Students"\
          " SET AverageGrade = ?, QuestionsCompleted = ?, GradeInt = ?"\
          " WHERE StudentID = ?"
    cursor.execute(sql, (newGrade, newQuestionAmount, gradeInt, studentID))
    db.commit()

    updateClassAverage(studentID)

def updateStudentPassword(password, studentID, salt):
    sql = "UPDATE Students"\
          " SET Pass = ?, Salt = ?"\
          " WHERE StudentID =?"
    db =sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (password, salt, studentID,))
    db.commit()

def deleteStudent(studentID):
    sql = "DELETE FROM Students"\
          " WHERE StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (studentID,))
    db.commit()

def getStudentDetails(studentID):
    ## Returns specific details relating to the questions a single student has completed
    sql1 = "SELECT Forename, Surname, ClassID, AverageGrade, QuestionsCompleted"\
           " FROM Students"\
           " WHERE StudentID = ?"

    sql2 = "SELECT Completed.DateCompleted, Completed.GradeAchieved, Completed.MarkAchieved, Questions.*"\
          " FROM Students, Questions, Completed"\
          " WHERE Students.StudentID = ? and"\
		" Students.StudentID = Completed.StudentID and"\
	 	" Completed.QuestionID = Questions.QuestionID"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql1, (studentID,))
    studentPersonal = cursor.fetchone()
    cursor.execute(sql2, (studentID,))
    studentQuestions = cursor.fetchall()

    return studentPersonal, studentQuestions


############################### Class functions #####################################

def getClasses():
    sql = "SELECT *"\
          " FROM Classes"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)
    classes = cursor.fetchall()
    return classes

def __addClasses():
    ## Finds classes that dont exist and adds them to the database
    classesList = getClasses()
    classes = [("Pink",), ("Yellow",), ("Red",), ("Blue",), ("Green",)]
    existingClasses = [Class[0] for Class in classesList]
    classesToCreate = []
    for item in classes:
        if item[0] not in existingClasses:
            classesToCreate.append(item)
    sql = "INSERT INTO Classes"\
          " Values(?, 'jdare', 'U')"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.executemany(sql, classesToCreate)
    db.commit()

def updateClass(classID, tutorID):
    sql = "UPDATE Classes"\
          " SET TutorID =?"\
          " WHERE ClassID = ?"

    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (tutorID, classID))
    db.commit()

def getClass(classID):
    ## Returns details about a specific class such as average grade, tutor etc
    sql1 = "SELECT Classes.*, Tutors.Forename, Tutors.Surname"\
          " FROM Classes, Tutors"\
          " WHERE Classes.ClassID = ?"\
          " AND Classes.TutorID = Tutors.TutorID"
    sql2 = "SELECT Students.Surname, Students.Forename, Students.AverageGrade"\
           " FROM Students"\
           " WHERE ClassID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql1, (classID,))
    info = cursor.fetchone()
    cursor.execute(sql2, (classID,))
    students = cursor.fetchall()
    return info, students

def updateClassAverage(classID):
    ## Updates the class's average grade 
    students = getStudentsByClass(classID)
    gradeInt = 0
    grades = ['U', 'E', 'D', 'C', 'B', 'A', 'A*']
    for student in students:
        gradeInt += grades.index(student[3])
    if len(students) == 0:
        gradeInt = 0
    else:
        gradeInt = round(gradeInt / len(students))
    avgGrade = grades[gradeInt]
    sql = "UPDATE Classes"\
          " SET ClassAverageGrade = ?"\
          " WHERE ClassID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (avgGrade, classID))
    db.commit()
    
############################# Tutor Functions ########################################

def getTutors():
    sql = "SELECT *"\
          " FROM Tutors"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql)
    tutors = cursor.fetchall()
    return tutors

def addTutor(tutorID, forename, surname, Pass, salt):
    sql = "INSERT INTO Tutors"\
          " VALUES(?,?,?,?,?)"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (tutorID, forename, surname, Pass, salt))
    db.commit()

def updateTutor(tutorID, forename, surname, password, salt):
    sql = "UPDATE Tutors"\
          " SET Forename = ?, Surname = ?, Pass = ?, Salt = ?"\
          " WHERE TutorID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (forename, surname, password, salt, tutorID))
    db.commit()

def getTutorByID(idno):
    sql = "SELECT Forename, Surname"\
          " FROM Tutors"\
          " WHERE TutorID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (idno,))
    tutorInfo = cursor.fetchone()
    return tutorInfo

def getTutorsBySurname(surname):
    sql = "SELECT *"\
          " FROM Tutors"\
          " WHERE Surname like ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, ("%"+surname+"%",))
    tutors = cursor.fetchall()
    return tutors

def deleteTutor(tutorID):
    sql = "DELETE FROM Tutors"\
          " WHERE TutorID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (tutorID,))
    db.commit()

############################Questions Functions########################################

def getQuestions():
    sql = "SELECT *"\
          " FROM Questions"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, ())
    questionsList = cursor.fetchall()
    return questionsList

def addQuestion(maxMark, fileName):
    sql = "INSERT INTO Questions(MaxMark, FileName)"\
          " VALUES(?, ?)"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (maxMark, fileName))
    db.commit()

def updateQuestion(maxMark, fileName):
    sql = "UPDATE Questions"\
          " SET MaxMark = ?, FileName = ?"\
          " WHERE FileName = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (maxMark, fileName, fileName))
    db.commit()

def deleteQuestion(fileName):
    sql = "DELETE FROM Questions"\
          " WHERE FileName = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (fileName,))
    db.commit()

def getAnsweredQuestions(studentID):
    ## Returns a list of all questions answered by the user with the most recent
    ## grade that they have achieved
    sql = "SELECT q.FileName, c.GradeAchieved"\
          " FROM Completed AS c, Questions as q"\
          " INNER JOIN (SELECT FileName, StudentID, max(DateCompleted) AS maxDate"\
          " FROM Completed LEFT JOIN Questions"\
          " ON Completed.QuestionID = Questions.QuestionID"\
          " GROUP BY StudentID, FileName )m"\
          " ON m.StudentID = c.StudentID AND m.maxDate = c.DateCompleted"\
          " WHERE C.QuestionID = Q.QuestionID "\
          " AND c.StudentID = ?"\
          " ORDER BY c.StudentID, q.FileName ASC"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (studentID,))
    data = cursor.fetchall()
    return data

def getFirstDateQuestionAnswered(studentID):
    sql = "SELECT min(DateCompleted)"\
          " FROM Completed, Students, Questions"\
          " WHERE Completed.StudentID == Students.StudentID"\
          " AND Questions.QuestionID == Completed.QuestionID"\
          " and Students.StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql, (studentID,))
    date = cursor.fetchone()
    return date[0]

def getGradesInDateRange(startDate, endDate, studentID):
    sql = "SELECT GradeAchieved"\
          " FROM Completed"\
          " WHERE DateCompleted >= ?"\
          " AND DateCompleted < ?"\
          " AND StudentID = ?"
    db = sqlite3.connect(__DBLOC)
    cursor =db.cursor()
    cursor.execute(sql, (startDate, endDate, studentID,))
    grades = cursor.fetchall()
    return grades

############################################################################

def checkUserExists(user):
    ## Checks to see if a user with an id 'user' exists within the database
    ## If they do, return True, with the type of user they are (student or tutor)
    ## Otherwise, return False with no type
    sql1 = "SELECT StudentID"\
           " FROM Students"
    sql2 = "SELECT TutorID"\
           " FROM Tutors"
    db = sqlite3.connect(__DBLOC)
    cursor = db.cursor()
    cursor.execute(sql1, ())
    studentIDs = [x[0] for x in cursor.fetchall()]
    cursor.execute(sql2, ())
    tutorIDs = [x[0] for x in cursor.fetchall()]

    if user in studentIDs:
        return True, "Student"
    elif user in tutorIDs:
        return True, "Tutor"
    else:
        return False, ""

def checkUserLogin(inUser, inPass):
    ## If a user with user ID 'inUser' exists then check if the entered password
    ## matches the one stored in the database
    ## In order to do this, the hashing algorithm is used along with the salt
    ## stored in the user's record
    exists, userType = checkUserExists(inUser)
    if exists:
        if userType == "Student":
            sql = "SELECT Pass, Salt FROM Students WHERE StudentID = ?"
            db = sqlite3.connect(__DBLOC)
            cursor = db.cursor()
            cursor.execute(sql, (inUser,))
            studentPass,studentSalt = cursor.fetchone()
            toHash = inPass+studentSalt
            digest = h.Hash(toHash)
            if studentPass == digest:
                return True, "Student"
            else:
                return False, ""
        elif userType == "Tutor":
            sql = "SELECT Pass, Salt FROM Tutors WHERE TutorID = ?"
            db = sqlite3.connect(__DBLOC)
            cursor = db.cursor()
            cursor.execute(sql, (inUser,))
            tutorPass, tutorSalt = cursor.fetchone()
            toHash = inPass+tutorSalt
            digest = h.Hash(toHash)
            if tutorPass == digest:
                return True, "Tutor"
            else:
                return False, ""
    else:
        return False, ""

if __name__ == "dbmanager":
    __createTables()
