from os import system
from rich import print
from rich.table import Table
from rich.prompt import Confirm
from mysql.connector import IntegrityError, DataError
import config
import pwinput
from student_functions import _view_student_results


def admin_auth():
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Admin Authentication")
        print("-" * 32)

        print("\n")
        print("1. Return to Home Screen")
        print("2. Sign in")

        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                break
            elif choice == 2:
                _login()
                continue
            else:
                raise ValueError
        except ValueError:
            print("[red]Error: Invalid Input")
        except config.LoginError:
            pass
        except KeyboardInterrupt:
            print("\n[red]Cancelled operation")
            pass

        config.wait_for_enter()

def _login():
    print("\n")
    uid = input("Enter your user id: ")
    pwd = pwinput.pwinput("Enter your password: ")

    config.cur.execute("select pwd from admins where uid = '{}';".format(uid))
    users = config.cur.fetchall()

    if len(users) == 0 or users[0][0] != pwd: # type: ignore
        print("[red]Error: Incorrect user id or password")
        raise config.LoginError

    print("[green]Logged in successfully!")

    _admin_home(uid)

def _admin_home(uid):
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Welcome {}!".format(uid))
        print("-" * 32)

        print("\n")
        print("1. Logout")
        print("2. View students")
        print("3. View exams")
        print("4. View subjects")
        print("5. View exam series")
        print("6. View results")
        print("7. Add exam")
        print("8. Add subject")
        print("9. Add exam series")
        print("10. Add results")
        print("11. Reset student password")

        # TODO Ability to edit entered data

        try:
            choice = int(input("Enter your choice: "))
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
            print("[red]Error: Invalid Input")
        except KeyboardInterrupt:
            print("\n[red]Cancelled operation")
            pass

        config.wait_for_enter()

def _view_student_list():

    print("\n")

    config.cur.execute("select rollno, name from students order by rollno")
    result = config.cur.fetchall()

    if len(result) == 0:
        print("[red]No registered students")
        return
    
    table = Table(title="Student List")

    table.add_column("Roll Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="spring_green3")

    for row in result:
        table.add_row(str(row[0]), row[1]) # type: ignore

    print(table)

def _view_exams():

    print("\n")

    config.cur.execute("select eid, series_id, date, sub_max_marks from exams order by date")
    result = config.cur.fetchall()

    if len(result) == 0:
        print("[red]No exams added")
        return
    
    table = Table(title="Exam List")

    table.add_column("Exam ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Series", style="spring_green3")
    table.add_column("Date", style="magenta", justify="right")
    table.add_column("Maximum Marks", style="gold3", justify="right")
    table.add_column("Subjects")


    for row in result:
        config.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(row[0])) # type: ignore
        sub_details = config.cur.fetchall()

        sub_table = Table.grid(expand=True, padding=(0, 4))
        sub_table.add_column(style="green4", justify="right")
        sub_table.add_column(style="turquoise2")

        for sub in sub_details:
            sub_table.add_row(sub[0], sub[1]) # type: ignore

        table.add_row(str(row[0]), row[1], row[2].strftime("%Y-%m-%d"), str(row[3] * len(sub_details)), sub_table) # type: ignore

    print(table)

def _view_subjects():
    print("\n")

    config.cur.execute("select sid, name from subjects order by sid")
    result = config.cur.fetchall()

    if len(result) == 0:
        print("[red]No subjects added")
        return
    
    table = Table(title="Subjects List")

    table.add_column("Subject ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Subject Name", style="spring_green3")

    for row in result:
        table.add_row(row[0], row[1]) # type: ignore

    print(table)

def _view_exam_series():
    print("\n")

    config.cur.execute("select series_id from series order by series_id")
    result = config.cur.fetchall()

    if len(result) == 0:
        print("[red]No series exist")
        return
    
    table = Table(title="Series List")

    table.add_column("Series ID", justify="right", style="cyan", no_wrap=True)

    for row in result:
        table.add_row(row[0]) # type: ignore

    print(table)

def _view_results():
    print("\n")

    print("1. Of exam")
    print("2. Of student")
    print("3. Of specific exam and student")

    try:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            _view_exam_results()
        elif choice == 2:
            _view_student_results_roll()
        elif choice == 3:
            _view_specific_result()
        else:
            raise ValueError
    except ValueError:
        print("[red]Error: Invalid Input")
        return
    except KeyboardInterrupt:
        print("\n[red]Cancelled Operation")
        return

def _view_exam_results():
    print("\n")

    eid = input("Exam ID: ")

    # Gets maximum possible marks and verifies that exam id exists
    try:
        config.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))

        records = config.cur.fetchall()
        if len(records) == 0:
            print("[red]Exam ID does not exist")
            raise
        
        sub_max_marks = records[0][0] # type: ignore
    except:
        print("[red]Error: Could not display result")
        return
    

    # Fetches subject details of exam

    try:
        config.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(eid))
        sub_details = config.cur.fetchall()
    except:
        print("[red]Error: Could not display result")
        return
    
    # Fetches sorted roll numbers of students in order of total marks

    try:
        config.cur.execute("select rollno, marks, ranking from results where eid='{}' and sid='000' order by marks".format(eid))
        roll_order = config.cur.fetchall()
        if len(roll_order) == 0:
            raise
    except:
        print("[red]No results found")
        return
    
    # Display the result

    table = Table()

    table.add_column("Roll Number", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="spring_green3")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")
    table.add_column("Subjects")

    for roll in roll_order:
        config.cur.execute("select name from students where rollno={}".format(roll[0])) #type: ignore
        name = config.cur.fetchall()[0][0] #type: ignore
        
        sub_table = Table(expand=True, padding=(0, 4), box=None)
        sub_table.add_column("Subject", style="green4")
        sub_table.add_column("Marks", style="turquoise2", justify="right")
        sub_table.add_column("Percentage", style="blue_violet", justify="right")
        sub_table.add_column("Rank", style="chartreuse3", justify="right")

        for sub in sub_details:
            config.cur.execute("select marks, ranking from results where rollno={} and eid ='{}' and sid='{}' order by sid".format(roll[0], eid, sub[0])) #type: ignore
            sub_results = config.cur.fetchall()[0]
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

    print(table)

def _view_student_results_roll():
    print("\n")

    rollno = int(input("Roll Number: "))

    try:
        config.cur.execute("select count(*) from students where rollno = {}".format(rollno))
        if config.cur.fetchall()[0][0] == 0: #type: ignore
            print("[red]Student with specified roll number does not exist")
            raise
    except:
        print("[red]Error: Could not display results")
        return

    _view_student_results(rollno)

def _view_specific_result():
    print("\n")

    eid = input("Exam ID: ")
    rollno = int(input("Roll Number: "))


    try:
        config.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))
        sub_max_marks = config.cur.fetchall()[0][0] #type: ignore

        config.cur.execute("select subjects.name, results.marks, results.ranking from subjects, results where rollno={} and eid='{}' and subjects.sid = results.sid order by results.sid".format(rollno, eid))
        sub_details = config.cur.fetchall()

        if len(sub_details) == 0:
            print("[red]No such results")
            raise
    except:
        print("[red]Error: Could not display result")
        return
    
    table = Table()

    table.add_column("Subject", style="green4")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")


    for sub in sub_details:
        percentage = sub[1] / sub_max_marks                                     #type: ignore
        if sub[0] == "Total":                                                   #type: ignore
            percentage /= len(sub_details) - 1

        percentage = int(percentage * 10000) / 100                              #type: ignore
        table.add_row(sub[0], str(sub[1]), str(percentage), str(sub[2] if not sub[2] is None else "-"))    #type: ignore

    print(table)

def _add_exam():
    
    print("\n")

    # Accept exams table data from user

    eid = input("Exam ID: ")
    series_id = input("Series ID: ")
    date = input("Enter Date (YYYY-MM-DD): ")
    sub_max_marks = int(input("Maximum marks per subject: "))

    # Accept subjects of the exam
    
    sub_codes = set()
    while True:
        sub_code = input("Add subject code (leave blank to finish): ")
        if sub_code == "":
            if len(sub_codes) == 0:
                print("[red]Atleast one subject must be added")
            else:
                break

        sub_codes.add(sub_code)

    # Add data into the exams table

    try:
        config.cur.execute("insert into exams values('{}', '{}', '{}', {})".format(eid, series_id, date, sub_max_marks))
        config.con.commit()
    except IntegrityError:
        print("[red]Exam ID taken or Series ID does not exist")
        print("[red]Error: Could not add exam")
        return
    except DataError:
        print("[red]Invalid date format entered")
        print("[red]Error: Could not add exam")
        return
    except:
        print("[red]Error: Could not add exam")
        return
    
    # Add data into the exam_subjects table

    success = True
    for sub_code in sub_codes:
        try:
            config.cur.execute("insert into exam_subjects values('{}', '{}')".format(eid, sub_code))
            config.con.commit()
        except IntegrityError:
            print("[red]Subject with code [blue]" + sub_code + "[/blue] does not exist")
            print("[red]Error: Could not add exam, failed to add subjects")
            success = False
            break
        except:
            print("[red]Error: Could not add exam, failed to add subejcts")
            success = False
            break
    
    # Report success

    if success:
        print("[green]Exam added successfully")
        return
    
    # Handle failure: remove exam data since addition into exam_subjects was unsucessful
    config.cur.execute("delete from exams where eid='{}'".format(eid))
    config.cur.execute("delete from exam_subjects where eid='{}'".format(eid))
    config.con.commit()

def _add_subject():

    print("\n")

    sid = input("Subject ID: ")
    name = input("Subject Name: ")

    try:
        config.cur.execute("insert into subjects values('{}', '{}')".format(sid, name))
        config.con.commit()
    except IntegrityError:
        print("[red]Subject ID taken")
        print("[red]Could not add subject")
    except:
        print("[red]Could not add subject")
    else:
        print("[green]Subject added successfully")

def _add_series():

    print("\n")

    series_id = input("Series ID: ")

    try:
        config.cur.execute("insert into series values('{}')".format(series_id))
        config.con.commit()
    except IntegrityError:
        print("[red]Series ID taken")
        print("[red]Could not add series")
    except:
        print("[red]Could not add series")
    else:
        print("[green]Series added successfully")


__add_result_previous_eid = None
__add_result_previous_rollno = None
def _add_result():

    print("\n")

    # Gets Exam ID and Roll Number from user

    global __add_result_previous_eid, __add_result_previous_rollno

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
        config.cur.execute("select count(*) from results where eid='{}' and rollno={}".format(eid, rollno))
        if config.cur.fetchall()[0][0] != 0: #type: ignore
            print("[red]Result already exists")
            raise
    except:
        print("[red]Error: Could not add result")
        return


    # Gets maximum marks per subject and verifies that exam id exists
    try:
        config.cur.execute("select sub_max_marks from exams where eid='{}'".format(eid))

        records = config.cur.fetchall()
        if len(records) == 0:
            print("[red]Exam ID does not exist")
            raise
        
        sub_max_marks = records[0][0] # type: ignore
    except:
        print("[red]Error: Could not add result")
        return
    
    # Verifies that student with specified roll number exists

    try:
        config.cur.execute("select count(*) from students where rollno={}".format(rollno))
        if config.cur.fetchall()[0][0] == 0: #type: ignore
            print("[red]Student with specified roll number does not exist")
            raise
    except:
        print("[red]Error: Could not add result")
        return

    # Gets subject details so user can be queried for information

    config.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid;".format(eid))

    sub_details = config.cur.fetchall()

    # Queries user for result

    ranking_applicable = Confirm.ask("Are rankings applicable to this result?")

    marks = []
    ranking = []
    for sub in sub_details:
        while True:
            print("Enter marks for [green4]" + sub[0] + "[/green4][turquoise2]" + sub[1] + "[/turquoise2]: ", end="") #type: ignore
            mark = int(input())
            if mark > sub_max_marks: #type: ignore
                print("[red]Entered marks exceed maximum marks")
                print("[red]Please try again")
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

    # Adds result to database

    try:
        if ranking_applicable:
            for i in range(len(marks)):
                config.cur.execute("insert into results values('{}', '{}', {}, {}, {})".format(eid, sub_details[i][0], rollno, marks[i], ranking[i])) #type: ignore
            config.cur.execute("insert into results values('{}', '{}', {}, {}, {})".format(eid, '000', rollno, sum(marks), ranking[len(marks)]))
        else:
            for i in range(len(marks)):
                config.cur.execute("insert into results values('{}', '{}', {}, {}, null)".format(eid, sub_details[i][0], rollno, marks[i])) #type: ignore
            config.cur.execute("insert into results values('{}', '{}', {}, {}, null)".format(eid, '000', rollno, sum(marks)))
        
        config.con.commit()
    except:
        print("[red]Error: Could not add result")
        return

    print("[green]Result added successfully")

    # Updates previous data for easy entry
    __add_result_previous_eid = eid
    __add_result_previous_rollno = rollno

def _reset_student_password():
    print("\n")

    rollno = int(input("Roll Number: "))

    try:
        config.cur.execute("select count(*) from students where rollno={}".format(rollno))
        if config.cur.fetchall()[0][0] == 0:  #type: ignore
            print("[red]Entered roll number does not exist")
            raise
    except:
        print("[red]Error: Could not update password")
        return

    pwd = pwinput.pwinput("Enter new password: ")
    re_pwd = pwinput.pwinput("Confirm new password: ")

    if pwd != re_pwd:
        print("[red]New password and confirmed password to not match")
        print("[red]Did not update password")
        return

    try:
        config.cur.execute("update students set pwd='{}' where rollno={}".format(pwd, rollno))
        config.con.commit()
    except:
        print("[red]Error: Could not update password")
        return
    
    print("[green]Password updated successfully!")

