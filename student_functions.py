from datetime import date, datetime
from mysql.connector import Error, IntegrityError
from os import system
from rich import print
import pwinput
from rich.prompt import Confirm
from rich.table import Table

import cfg
import db_utils
import graphing_utils


def student_auth():
    """
    Entry point for students
    """
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Student Authentication")
        print("-" * 32)

        print("\n")
        print("1. Return to Home Screen")
        print("2. Login")
        print("3. Sign up")
        print()


        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                break
            elif choice == 2:
                _login()
                continue
            elif choice == 3:
                _signup()
            else:
                raise ValueError
        except ValueError:
            cfg.failure("Invalid Input")
        except cfg.LoginError:
            pass
        except KeyboardInterrupt:
            cfg.failure("\nCancelled operation")
            pass

        cfg.wait_for_enter()


def _login():
    """
    Verifies student login credential and redirects to the student's homepage if successful

    Raises
    ------
    cfg.LoginError
        If the credentials are not valid
    """

    print("\n")

    #Inputs student details
    rollno = int(input("Enter your roll number: "))
    pwd = pwinput.pwinput("Enter your password (contact admin if you forgot): ")

    #Fetches data from database
    cfg.cur.execute("select pwd, name from students where rollno = {};".format(rollno))
    users: list[tuple[str, str]] = cfg.cur.fetchall() #type: ignore

    #Checks if credentials are valid
    if len(users) == 0 or users[0][0] != pwd:
        cfg.failure("Incorrect roll number or password")
        raise cfg.LoginError

    #Redirects to student homepage
    cfg.success("Logged in successfully!")
    _student_home(rollno, users[0][1])

def _signup():
    """
    Creates a new student profile
    """

    print("\n")

    #Inputs student details
    rollno = int(input("Enter your roll number: "))
    name = input("Enter your name: ")
    pwd = pwinput.pwinput("Enter a password: ")
    re_pwd = pwinput.pwinput("Confirm your password: ")


    if pwd != re_pwd:
        cfg.failure("Could not create profile")
        cfg.failure("Password and confirmed password do not match")
        return

    #Attempts to create profile
    try:
        if db_utils.check_student_exists(rollno):
            cfg.failure("Roll number taken")
            raise

        cfg.cur.execute("insert into students values({}, '{}', '{}')".format(rollno, name, pwd))
        cfg.con.commit()
    except:
        cfg.failure("Could not create profile")
        return
    
    cfg.success("Profile created successfully!")

def _student_home(rollno: int, name: str):
    """
    Homepage for students

    Parameters
    ----------
    rollno : int
        Roll number of student, used in further queries
    name: str
        Name of student, used only for welcome message
    """
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Welcome {}!".format(name))
        print("-" * 32)

        print("\n")
        print("1. Logout")
        print("2. View results")
        print("3. Display graphs")
        print("4. Analyse results")
        print("5. Update password")
        print("6. Delete profile")
        print()


        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                break
            elif choice == 2:
                _view_student_results(rollno)
            elif choice == 3:
                _view_student_graphs(rollno)
            elif choice == 4:
                _view_analysis(rollno)
            elif choice == 5:
                _update_password(rollno)
            elif choice == 6:
                _delete_account(rollno)
            else:
                raise ValueError
        except ValueError:
            cfg.failure("Invalid Input")
        except cfg.AccountDeleted:
            break
        except KeyboardInterrupt:
            cfg.failure("\nCancelled operation")
            pass

        cfg.wait_for_enter()    


def _view_student_results(rollno: int):
    """
    Lets students access their results

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch the results
    """

    print("\n")

    #Asks user for additional details
    series = input("Series (leave blank to display all): ")

    #Fetches the results of exams given by student
    if series == "":
        query = "select results.eid, exams.date, exams.series_id, results.marks, marks_percentage(results.eid, results.sid, results.rollno), results.ranking from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid order by exams.date desc".format(rollno)
    else:
        query = "select results.eid, exams.date, exams.series_id, results.marks, marks_percentage(results.eid, results.sid, results.rollno), results.ranking from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid and exams.series_id = '{}' order by exams.date desc".format(rollno, series)

    try:
        cfg.cur.execute(query)
        exam_list: list[tuple[str, date, str, int, float, int]] = cfg.cur.fetchall() #type: ignore
        if len(exam_list) == 0:
            cfg.failure("No results found")
            raise
    except:
        cfg.failure("Could not fetch results")
        return

    #Displays the result

    #--Creates table to display the result
    table = Table()

    table.add_column("Exam ID", style="cyan", no_wrap=True)
    table.add_column("Date", style="deep_pink4")
    table.add_column("Series", style="spring_green3")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")
    table.add_column("Subjects")

    #--Adds a row for result of each exam
    for exam in exam_list:
        #-- --Fetches subject list of specific exam
        try:
            sub_details = db_utils.fetch_subject_list_by_exam(exam[0], include_total=False)
        except:
            cfg.failure("Could not display result")
            return

        #-- --Creates sub-table for subject-wise results
        sub_table = Table(expand=True, padding=(0, 4), box=None)
        sub_table.add_column("Subject ID", style="green4")
        sub_table.add_column("Subject", style="turquoise2")
        sub_table.add_column("Marks", style="red3", justify="right")
        sub_table.add_column("Percentage", style="blue_violet", justify="right")
        sub_table.add_column("Rank", style="chartreuse3", justify="right")

        #-- -- --Fetches subject-wise details and adds it to the sub-table
        for sub in sub_details:
            cfg.cur.execute("select marks, ranking, marks_percentage(eid, sid, rollno) from results where rollno={} and eid ='{}' and sid='{}'".format(rollno, exam[0], sub[1]))
            sub_results: list[tuple[int, int, float]] = cfg.cur.fetchall()[0] #type: ignore
            sub_table.add_row(
                sub[1],
                sub[0],
                str(sub_results[0]),
                "{:.2f}".format(sub_results[2] * 100),
                str(sub_results[1] if not sub_results[1] is None else "-")
            ) 

        ##-- --Adds exams to the table
        table.add_row(
            exam[0],
            exam[1].strftime('%Y-%m-%d'),
            exam[2],
            str(exam[3]),
            "{:.2f}".format(exam[4] * 100),
            str(exam[5] if not exam[5] is None else "-"),
            sub_table
        )

    ##--Display the created table
    print(table)    


def _view_student_graphs(rollno: int):
    """
    Lets students view various graphs of their results

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch the results
    """

    series = input("Series (leave blank to use all): ")
    subject_id = input("Subject ID (leave blank to use overall): ")

    if subject_id == "":
        subject = ("000", "Overall")
    else:
        sub_name = db_utils.fetch_subject_name(subject_id)
        if sub_name is None:
            cfg.failure("No such subjects")
            return
        subject = (subject_id, sub_name)

    print("1. Percentage-Exam Line Graph")
    print("2. Frequency-Percentage Bar Graph")
    print("3. Percentage Probability Distribution")
    print()

    try:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            graphing_utils.student_result_line_graph(rollno, series, subject)
        elif choice == 2:
            graphing_utils.student_result_frequency_plot(rollno, series, subject)
        elif choice == 3:
            graphing_utils.student_result_distribution(rollno, series, subject)
        else:
            raise ValueError
    except ValueError:
        cfg.failure("Invalid Input")
    except KeyboardInterrupt:
        cfg.failure("\nCancelled Operation")



def _view_analysis(rollno: int):
    """
    Lets students analyse their results

    Parameters
    ----------
    rollno : int
        Roll number of student, used to fetch the results
    """

    print("\n")

    #Asks user for additional details
    series = input("Series (leave blank to use all): ")
    recent_count = int(input("Number of exams to be considered in recent: "))
    
    #Fetches subject list of student
    try:
        subject_list = db_utils.fetch_subject_list_by_student_series(rollno, series)
        if len(subject_list) == 0:
            cfg.failure("No such results in records")
            raise
    except:
        cfg.failure("Could not fetch subject details")

    

    #Creates table to display the results
    table = Table()

    table.add_column("Subject", style="green4")
    table.add_column("Average Percentage", style="spring_green3", justify="right")
    table.add_column("Percentage Standard Deviation", style="gold3", justify="right")
    table.add_column("Recent Average Percentage", style="light_sea_green", justify="right")
    table.add_column("Recent Percentage Standard Deviation", style="magenta", justify="right")

    #Adds a row for each subject
    for sub in subject_list:

        #Uses user defined sql functions to fetch marks percentage
        if series == "":
            query = "select avg(marks_percentage(results.eid, '{0}', {1})), stddev(marks_percentage(results.eid, '{0}', {1})) from results".format(sub[1], rollno)
        else:
            query = "select avg(marks_percentage(results.eid, '{0}', {1})), stddev(marks_percentage(results.eid, '{0}', {1})) from results, exams where results.eid = exams.eid and exams.series_id = '{2}'".format(sub[1], rollno, series)
        cfg.cur.execute(query)
        overall_data: tuple[float, float] = cfg.cur.fetchall()[0] #type: ignore

        if series == "":
            query = "select avg(marks_percentage(results.eid, '{0}', {1})), stddev(marks_percentage(results.eid, '{0}', {1})) from results, exams where results.eid = exams.eid and results.sid = '{0}' and results.rollno = {1} order by exams.date limit {2}".format(sub[1], rollno, recent_count)
        else:
            query = "select avg(marks_percentage(results.eid, '{0}', {1})), stddev(marks_percentage(results.eid, '{0}', {1})) from results, exams where results.eid = exams.eid and results.sid = '{0}' and results.rollno = {1} and exams.series_id = '{3}' order by exams.date limit {2}".format(sub[1], rollno, recent_count, series)
        cfg.cur.execute(query)
        recent_data: tuple[float, float] = cfg.cur.fetchall()[0] #type: ignore

        table.add_row(sub[0], "{:.2f}".format(overall_data[0] * 100), "{:.2f}".format(overall_data[1] * 100), "{:.2f}".format(recent_data[0] * 100), "{:.2f}".format(recent_data[1] * 100))

    #Displays the result
    print(table)


def _update_password(rollno: int):
    """
    Updates student's password

    Parameters
    ----------
    rollno : int
        Roll number of student, used to identify student for updation
    """

    print("\n")

    #Confirms student's identity
    pwd = pwinput.pwinput("Please enter current password: ")
    cfg.cur.execute("select pwd from students where rollno = {}".format(rollno))

    if pwd != cfg.cur.fetchall()[0][0]: # type: ignore
        cfg.failure("Incorrect password")
        return
    
    #Inputs new password
    new_pwd = pwinput.pwinput("Enter new password: ")
    re_new_pwd = pwinput.pwinput("Confirm new password: ")

    if new_pwd != re_new_pwd:
        cfg.failure("Did not update passsword")
        cfg.failure("Password and confirmed password do not match")
        return
    
    #Updates the database
    cfg.cur.execute("update students set pwd='{}' where rollno={}".format(new_pwd, rollno))
    cfg.con.commit()

    cfg.success("Password updated successfully")

def _delete_account(rollno: int):
    """
    Deletes student's profile

    Parameters
    ----------
    rollno : int
        Roll number of student, used to identify student for deletion

    Raises
    ------
    cfg.AccountDeleted
        If account is successfully deleted.
        Not an actual error, but used to exit out of the student homepage loop
    """

    print("\n")
    
    #Displays warning to student
    print("[red bold]This action is irreversible")
    confirmed = Confirm.ask("[blue bold]Are you sure you wish to delete your profile?")
    if not confirmed:
        return
    
    #Confirms student's identiy
    pwd = pwinput.pwinput("Please enter password for verification: ")
    cfg.cur.execute("select pwd from students where rollno = {}".format(rollno))

    if pwd != cfg.cur.fetchall()[0][0]: # type: ignore
        cfg.failure("Incorrect password")
        return
    
    #Deletes account
    cfg.cur.execute("delete from students where rollno={}".format(rollno))
    cfg.con.commit()

    cfg.success("Profile deleted successfully")

    cfg.wait_for_enter()

    raise cfg.AccountDeleted


