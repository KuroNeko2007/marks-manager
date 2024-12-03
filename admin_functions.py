from mysql.connector import IntegrityError, DataError
from os import system
import pwinput
from rich import print
from rich.table import Table
from rich.prompt import Confirm

import cfg
from student_functions import _view_student_results


def admin_auth():
    """
    Entry point for admins
    """
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Admin Authentication")
        print("-" * 32)

        print("\n")
        print("1. Return to Home Screen")
        print("2. Sign in")
        print()

        try:
            choice = int(input("Enter your choice: "))

            print("\n")
            if choice == 1:
                break
            elif choice == 2:
                _login()
                continue
            else:
                raise ValueError
        except ValueError:
            cfg.failure("Error: Invalid Input")
        except cfg.LoginError:
            pass
        except KeyboardInterrupt:
            cfg.failure("\nCancelled operation")
            pass

        cfg.wait_for_enter()

def _login():
    """
    Verifies admin login credential and redirects to the admin's homepage if successful

    Raises
    ------
    cfg.LoginError
        If the credentials are not valid
    """
    uid = input("Enter your user id: ")
    pwd = pwinput.pwinput("Enter your password: ")

    cfg.cur.execute("select pwd from admins where uid = '{}';".format(uid))
    users = cfg.cur.fetchall()

    if len(users) == 0 or users[0][0] != pwd: # type: ignore
        cfg.failure("Error: Incorrect user id or password")
        raise cfg.LoginError

    cfg.success("Logged in successfully!")

    _admin_home(uid)

def _admin_home(uid):
    """
    Homepage for admins

    Parameters
    ----------
    uid : str
        User id of admin, used only for welcome message
    """
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Welcome {}!".format(uid))
        print("-" * 32)

        print("\n")
        print("1. Logout")
        print()
        print("2. View students")
        print("3. View exams")
        print("4. View subjects")
        print("5. View exam series")
        print("6. View results")
        print()
        print("7. Add exam")
        print("8. Add subject")
        print("9. Add exam series")
        print("10. Add results")
        print()
        print("11. Reset student password")
        print()

        # TODO Ability to edit entered data

        try:
            choice = int(input("Enter your choice: "))

            print("\n")
            if choice == 1:
                break
            elif choice == 2:
                _view_student_list()
            elif choice == 3:
                _view_exams()
            elif choice == 4:
                _view_subjects()
            elif choice == 5:
                _view_exam_series()
            elif choice == 6:
                _view_results()
            elif choice == 7:
                _add_exam()
            elif choice == 8:
                _add_subject()
            elif choice == 9:
                _add_series()
            elif choice == 10:
                _add_result()
            elif choice == 11:
                _reset_student_password()
            else:
                raise ValueError
        except ValueError:
            cfg.failure("Error: Invalid Input")
        except KeyboardInterrupt:
            cfg.failure("\nCancelled operation")
            pass

        cfg.wait_for_enter()

def _view_student_list():
    """
    Displays list of students
    """

    #Fetches list of students
    try:
        cfg.cur.execute("select rollno, name from students order by rollno")
        students = cfg.cur.fetchall()

        if len(students) == 0:
            cfg.failure("No students in records")
            raise
    except:
        cfg.failure("Could not fetch student details")
        return


    #Displays list of students
    table = Table(title="Student List")

    table.add_column("Roll Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="spring_green3")

    for student in students:
        table.add_row(str(student[0]), student[1]) # type: ignore

    print(table)

def _view_exams():
    """
    Displays list of exams
    """

    #Fetches list of exams
    try:
        cfg.cur.execute("select eid, series_id, date, sub_max_marks from exams order by date")
        result = cfg.cur.fetchall()

        if len(result) == 0:
            cfg.failure("No exams in records")
            raise
    except:
        cfg.failure("Could not fetch exam details")
        return

    #Creates table to display exams
    table = Table(title="Exam List")

    table.add_column("Exam ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Series", style="spring_green3")
    table.add_column("Date", style="magenta", justify="right")
    table.add_column("Maximum Marks", style="gold3", justify="right")
    table.add_column("Subjects")


    #Adds each exam to the table
    for row in result:
        cfg.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(row[0])) # type: ignore
        sub_details = cfg.cur.fetchall()

        #--Creates sub table to handle subject details
        sub_table = Table.grid(expand=True, padding=(0, 4))
        sub_table.add_column(style="green4", justify="right")
        sub_table.add_column(style="turquoise2")

        for sub in sub_details:
            sub_table.add_row(sub[0], sub[1]) # type: ignore

        table.add_row(str(row[0]), row[1], row[2].strftime("%Y-%m-%d"), str(row[3] * len(sub_details)), sub_table) # type: ignore

    #Displays table
    print(table)

def _view_subjects():
    """
    Displays list of subjects
    """

    #Fetches list of subjects
    try:
        cfg.cur.execute("select sid, name from subjects order by sid")
        result = cfg.cur.fetchall()

        if len(result) == 0:
            cfg.failure("No subjects in records")
            raise
    except:
        cfg.failure("Could not fetch subject details")
        return
        
    #Displays list of subjects
    table = Table(title="Subjects List")

    table.add_column("Subject ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Subject Name", style="spring_green3")

    for row in result:
        table.add_row(row[0], row[1]) # type: ignore

    print(table)

def _view_exam_series():
    """
    Displays list of series
    """

    #Fetches list of series
    try:
        cfg.cur.execute("select series_id from series order by series_id")
        result = cfg.cur.fetchall()

        if len(result) == 0:
            cfg.failure("No series in records")
            raise
    except:
        cfg.failure("Could not fetch series details")
        return

    #Displays list of series
    table = Table(title="Series List")
    table.add_column("Series ID", justify="right", style="cyan", no_wrap=True)

    for row in result:
        table.add_row(row[0]) # type: ignore

    print(table)

def _view_results():
    """
    Displays results according to user choice
    """

    #Inputs additional information
    print("1. Of exam")
    print("2. Of student")
    print("3. Of specific exam and student")
    print()

    try:
        choice = int(input("Enter your choice: "))

        print("\n")
        if choice == 1:
            _view_exam_results()
        elif choice == 2:
            _view_student_results_roll()
        elif choice == 3:
            _view_specific_result()
        else:
            raise ValueError
    except ValueError:
        cfg.failure("Error: Invalid Input")
        return
    except KeyboardInterrupt:
        cfg.failure("\nCancelled Operation")
        return

def _view_exam_results():
    """
    Displays result of a specific exam
    """

    #Inputs additional information
    eid = input("Exam ID: ")


    #Fetches maximum possible marks and verifies that exam id exists
    try:
        cfg.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))

        records = cfg.cur.fetchall()
        if len(records) == 0:
            cfg.failure("No such exam in records")
            raise
        
        sub_max_marks = records[0][0] # type: ignore
    except:
        cfg.failure("Could not fetch exam details")
        return
    

    #Fetches subject details of exam
    try:
        cfg.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(eid))
        sub_details = cfg.cur.fetchall()
    except:
        cfg.failure("Could not fetch subject details")
        return
    
    #Fetches sorted roll numbers of students in order of total marks
    try:
        cfg.cur.execute("select rollno, marks, ranking from results where eid='{}' and sid='000' order by marks".format(eid))
        roll_order = cfg.cur.fetchall()
        if len(roll_order) == 0:
            raise
    except:
        cfg.failure("Could not fetch student details")
        return
    
    #Creates table to the result
    table = Table()

    table.add_column("Roll Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="spring_green3")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")
    table.add_column("Subjects")

    #Adds students to the table
    try:
        for roll in roll_order:
            #Fetches specific student details
            cfg.cur.execute("select name from students where rollno={}".format(roll[0])) #type: ignore
            name = cfg.cur.fetchall()[0][0] #type: ignore
            
            sub_table = Table(expand=True, padding=(0, 4), box=None)
            sub_table.add_column("Subject", style="green4")
            sub_table.add_column("Marks", style="turquoise2", justify="right")
            sub_table.add_column("Percentage", style="blue_violet", justify="right")
            sub_table.add_column("Rank", style="chartreuse3", justify="right")

            for sub in sub_details:
                #Fetches specific subject details
                cfg.cur.execute("select marks, ranking from results where rollno={} and eid ='{}' and sid='{}' order by sid".format(roll[0], eid, sub[0])) #type: ignore
                sub_results = cfg.cur.fetchall()[0]
                sub_table.add_row(
                    sub[1],                                                         # type: ignore
                    str(sub_results[0]),                                            # type: ignore
                    str(int(10000 * sub_results[0] / sub_max_marks) / 100),         # type: ignore
                    str(sub_results[1] if not sub_results[1] is None else "-")      # type: ignore
                ) 

            table.add_row(
                str(roll[0]),                                                               # type: ignore
                name,                                                                       # type: ignore
                str(roll[1]),                                                               # type: ignore
                str(int(10000 * roll[1] / (len(sub_details) * sub_max_marks)) / 100),       # type: ignore
                str(roll[2] if not roll[2] is None else "-"),                               # type: ignore
                sub_table
            )
    except:
        cfg.failure("Could not fetch results")
        return
    

    print(table)

def _view_student_results_roll():
    """
    Displays result of a specific student
    """

    #Inputs additional details
    rollno = int(input("Roll Number: "))

    #Verifies that entered data is valid
    try:
        cfg.cur.execute("select count(*) from students where rollno = {}".format(rollno))
        if cfg.cur.fetchall()[0][0] == 0: #type: ignore
            cfg.failure("No such students in records")
            raise
    except:
        cfg.failure("Could not display results")
        return

    #Redirects to student functions with the specifed roll number
    _view_student_results(rollno)

def _view_specific_result():
    """
    Displays result of a specific exam and student
    """

    #Inputs additional details
    eid = input("Exam ID: ")
    rollno = int(input("Roll Number: "))

    #Fetches results
    try:
        cfg.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))
        exam_details = cfg.cur.fetchall()
        if len(exam_details) == 0:
            cfg.failure("No such exam in records")
            raise

        sub_max_marks = exam_details[0][0] #type: ignore

        cfg.cur.execute("select subjects.name, results.marks, results.ranking from subjects, results where rollno={} and eid='{}' and subjects.sid = results.sid order by results.sid".format(rollno, eid))
        sub_details = cfg.cur.fetchall()

        if len(sub_details) == 0:
            cfg.failure("No such results in records")
            raise
    except:
        cfg.failure("Could not display result")
        return
    
    #Creates table to display results
    table = Table()

    table.add_column("Subject", style="green4")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")

    #Adds information to table
    for sub in sub_details:
        percentage = sub[1] / sub_max_marks                                     #type: ignore
        if sub[0] == "Total":                                                   #type: ignore
            percentage /= len(sub_details) - 1

        percentage = int(percentage * 10000) / 100                              #type: ignore
        table.add_row(sub[0], str(sub[1]), str(percentage), str(sub[2] if not sub[2] is None else "-"))    #type: ignore

    #Displays table
    print(table)

def _add_exam():
    """
    Adds exam to database
    """

    #Inputs exams data
    eid = input("Exam ID: ")
    series_id = input("Series ID: ")
    date = input("Enter Date (YYYY-MM-DD): ")
    sub_max_marks = int(input("Maximum marks per subject: "))

    #Inputs subjects of the exam
    sub_codes = set()
    while True:
        sub_code = input("Add subject code (leave blank to finish): ")
        if sub_code == "":
            if len(sub_codes) == 0:
                cfg.failure("Atleast one subject must be added")
            else:
                break
        elif sub_code == "000":
            cfg.failure("The [blue1]Total[/blue1] gets added automatically")
            continue

        sub_codes.add(sub_code)

    #Add data into the exams table
    try:
        cfg.cur.execute("insert into exams values('{}', '{}', '{}', {})".format(eid, series_id, date, sub_max_marks))
        cfg.con.commit()
    except IntegrityError:
        cfg.failure("Exam ID taken or Series ID does not exist")
        cfg.failure("Could not add exam")
        return
    except DataError:
        cfg.failure("Invalid date format entered")
        cfg.failure("Could not add exam")
        return
    except:
        cfg.failure("Could not add exam")
        return
    
    #Add data into the exam_subjects table
    success = True
    for sub_code in sub_codes:
        try:
            cfg.cur.execute("insert into exam_subjects values('{}', '{}')".format(eid, sub_code))
            cfg.con.commit()
        except IntegrityError:
            cfg.failure("Subject with code [blue]" + sub_code + "[/blue] does not exist")
            cfg.failure("Could not add exam, failed to add subjects")
            success = False
            break
        except:
            cfg.failure("Could not add exam, failed to add subejcts")
            success = False
            break
    
    #Report success
    if success:
        cfg.success("Exam added successfully")
        return
    
    #Handle failure: remove exam data since addition into exam_subjects was unsucessful
    cfg.cur.execute("delete from exams where eid='{}'".format(eid))
    cfg.cur.execute("delete from exam_subjects where eid='{}'".format(eid))
    cfg.con.commit()

def _add_subject():
    """
    Adds subject to database
    """

    #Inputs additional details
    sid = input("Subject ID: ")
    name = input("Subject Name: ")

    #Adds subject to database
    try:
        cfg.cur.execute("insert into subjects values('{}', '{}')".format(sid, name))
        cfg.con.commit()
    except IntegrityError:
        cfg.failure("Subject ID taken")
        cfg.failure("Could not add subject")
    except:
        cfg.failure("Could not add subject")
    else:
        cfg.success("Subject added successfully")

def _add_series():
    """
    Adds series to database
    """

    #Inputs additional details
    series_id = input("Series ID: ")

    #Adds series to database
    try:
        cfg.cur.execute("insert into series values('{}')".format(series_id))
        cfg.con.commit()
    except IntegrityError:
        cfg.failure("Series ID taken")
        cfg.failure("Could not add series")
    except:
        cfg.failure("Could not add series")
    else:
        cfg.success("Series added successfully")


#Stores state for following function to ease bulk entry of results
__add_result_previous_eid = None
__add_result_previous_rollno = None
def _add_result():
    """
    Adds result to database
    """

    global __add_result_previous_eid, __add_result_previous_rollno

    #Inputs Exam ID and Roll Number from user
    if __add_result_previous_eid == None or __add_result_previous_rollno == None:
        eid = input("Exam ID: ")
        rollno = int(input("Roll Number: "))
    else:
        eid = input("Exam ID (leave blank to use previously entered): ")
        if eid == "":
            eid = __add_result_previous_eid

        rollno = input("Roll Number (leave blank to use previously entered): ")
        if rollno == "":
            rollno = __add_result_previous_rollno
        else:
            rollno = int(rollno)    
    

    #Verifies that result does not already exist
    try:
        cfg.cur.execute("select count(*) from results where eid='{}' and rollno={}".format(eid, rollno))
        if cfg.cur.fetchall()[0][0] != 0: #type: ignore
            cfg.failure("Result already exists")
            raise
    except:
        cfg.failure("Could not add result")
        return


    #Gets maximum marks per subject and verifies that exam id exists
    try:
        cfg.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))

        records = cfg.cur.fetchall()
        if len(records) == 0:
            cfg.failure("No such exam in records")
            raise
        
        sub_max_marks = records[0][0] # type: ignore
    except:
        cfg.failure("Could not add result")
        return
    

    #Verifies that student with specified roll number exists
    try:
        cfg.cur.execute("select count(*) from students where rollno={}".format(rollno))
        if cfg.cur.fetchall()[0][0] == 0: #type: ignore
            cfg.failure("No such student in records")
            raise
    except:
        cfg.failure("Could not add result")
        return

    #Fetches subject details so user can be queried for information
    cfg.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(eid))

    sub_details = cfg.cur.fetchall()

    #Inputs result
    ranking_applicable = Confirm.ask("Are rankings applicable to this result?")

    marks = []
    ranking = []
    for sub in sub_details:
        while True:
            print("Enter marks for [green4]" + sub[0] + "[/green4][turquoise2]" + sub[1] + "[/turquoise2]: ", end="") #type: ignore
            mark = int(input())
            if mark > sub_max_marks: #type: ignore
                cfg.failure("Entered marks exceed maximum marks")
                cfg.failure("Please try again")
                continue
            break

        if ranking_applicable:
                print("Enter rank for [green4]" + sub[0] + "[/green4][turquoise2]" + sub[1] + "[/turquoise2]: ", end="") #type: ignore
                rank = int(input())
                ranking.append(rank)
        marks.append(mark)
    
    if ranking_applicable:
        rank = int(input(("Enter overall rank: ")))
        ranking.append(rank)

    #Adds result to database
    try:
        if ranking_applicable:
            for i in range(len(marks)):
                cfg.cur.execute("insert into results values('{}', '{}', {}, {}, {})".format(eid, sub_details[i][0], rollno, marks[i], ranking[i])) #type: ignore
            cfg.cur.execute("insert into results values('{}', '{}', {}, {}, {})".format(eid, '000', rollno, sum(marks), ranking[len(marks)]))
        else:
            for i in range(len(marks)):
                cfg.cur.execute("insert into results values('{}', '{}', {}, {}, null)".format(eid, sub_details[i][0], rollno, marks[i])) #type: ignore
            cfg.cur.execute("insert into results values('{}', '{}', {}, {}, null)".format(eid, '000', rollno, sum(marks)))
        
        cfg.con.commit()
    except:
        cfg.failure("Error: Could not add result")
        return

    cfg.success("Result added successfully")

    #Updates state variables for easy entry
    __add_result_previous_eid = eid
    __add_result_previous_rollno = rollno

def _reset_student_password():
    """
    Resets password for specifed student
    """

    #Inputs additional details
    rollno = int(input("Roll Number: "))

    #Verifies that student with specifed roll number exist
    try:
        cfg.cur.execute("select count(*) from students where rollno={}".format(rollno))
        if cfg.cur.fetchall()[0][0] == 0:  #type: ignore
            cfg.failure("Entered roll number does not exist")
            raise
    except:
        cfg.failure("Error: Could not update password")
        return

    #Inputs password
    pwd = pwinput.pwinput("Enter new password: ")
    re_pwd = pwinput.pwinput("Confirm new password: ")

    if pwd != re_pwd:
        cfg.failure("New password and confirmed password to not match")
        cfg.failure("Did not update password")
        return

    #Updates password in database
    try:
        cfg.cur.execute("update students set pwd='{}' where rollno={}".format(pwd, rollno))
        cfg.con.commit()
    except:
        cfg.failure("Could not update password")
        return
    
    cfg.success("Password updated successfully!")

