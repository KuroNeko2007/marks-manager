from datetime import datetime
from mysql.connector import IntegrityError
from os import system
from rich import print
import pwinput
from rich.prompt import Confirm
from rich.table import Table

import cfg

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
    rollno = input("Enter your roll number: ")
    pwd = pwinput.pwinput("Enter your password (contact admin if you forgot): ")

    #Fetches data from database
    cfg.cur.execute("select pwd, name from students where rollno = '{}';".format(rollno))
    users = cfg.cur.fetchall()

    #Checks if credentials are valid
    if len(users) == 0 or users[0][0] != pwd: # type: ignore
        cfg.failure("Incorrect roll number or password")
        raise cfg.LoginError

    #Redirects to student homepage
    cfg.success("Logged in successfully!")
    _student_home(rollno, users[0][1]) # type: ignore

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
        cfg.cur.execute("insert into students values({}, '{}', '{}')".format(rollno, name, pwd))
        cfg.con.commit()
    except IntegrityError:
        cfg.failure("Roll number taken")
        cfg.failure("Could not create profile")
    except:
        cfg.failure("Could not create profile")
    else:
        cfg.success("Profile created successfully!")

def _student_home(rollno, name):
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
        print("3. Analyse results")
        print("4. Update password")
        print("5. Delete profile")
        print()


        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                break
            elif choice == 2:
                _view_student_results(rollno)
            elif choice == 3:
                _view_analysis(rollno)
            elif choice == 4:
                _update_password(rollno)
            elif choice == 5:
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


def _view_student_results(rollno):
    """
    Lets students access their results

    Parameters
    ----------
    rollno : int
        Roll number of students, used to fetch the results
    """

    print("\n")

    #Asks user for additional details
    series = input("Series (leave blank to display all): ")

    #Fetches the list of exams given by student
    if series == "":
        query = "select results.eid, exams.date, exams.series_id, results.marks, results.ranking, exams.sub_max_marks from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid order by exams.date desc".format(rollno)
    else:
        query = "select results.eid, exams.date, exams.series_id, results.marks, results.ranking, exams.sub_max_marks from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid and exams.series_id = '{}' order by exams.date desc".format(rollno, series)

    try:
        cfg.cur.execute(query)
        exam_list = cfg.cur.fetchall()
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
            cfg.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid order by exam_subjects.sid;".format(exam[0])) #type: ignore
            sub_details = cfg.cur.fetchall()
        except:
            cfg.failure("Could not display result")
            return

        #-- --Creates sub-table for subject-wise results
        sub_table = Table(expand=True, padding=(0, 4), box=None)
        sub_table.add_column("Subject", style="green4")
        sub_table.add_column("Marks", style="turquoise2", justify="right")
        sub_table.add_column("Percentage", style="blue_violet", justify="right")
        sub_table.add_column("Rank", style="chartreuse3", justify="right")

        #-- -- --Fetches subject-wise details and adds it to the sub-table
        for sub in sub_details:
            cfg.cur.execute("select marks, ranking from results where rollno={} and eid ='{}' and sid='{}'".format(rollno, exam[0], sub[0])) #type: ignore
            sub_results = cfg.cur.fetchall()[0]
            sub_table.add_row(
                sub[1],                                                         # type: ignore
                str(sub_results[0]),                                            # type: ignore
                str(int(10000 * sub_results[0] / exam[5]) / 100),         # type: ignore
                str(sub_results[1] if not sub_results[1] is None else "-")      # type: ignore
            ) 

        ##-- --Adds exams to the table
        table.add_row(
            exam[0],                                                            # type: ignore
            datetime.strftime(exam[1], '%Y-%m-%d'),                             # type: ignore
            exam[2],                                                            # type: ignore
            str(exam[3]),                                                       # type: ignore
            str(int(10000 * exam[3] / (len(sub_details) * exam[5])) / 100),     # type: ignore
            str(exam[4] if not exam[4] is None else "-"),                       # type: ignore
            sub_table
        )

    ##--Display the created table
    print(table)

def _view_analysis(rollno):
    """
    Lets students analyse their results

    Parameters
    ----------
    rollno : int
        Roll number of students, used to fetch the results
    """

    print("\n")

    #Asks user for additional details
    series = input("Series (leave blank to use all): ")
    recent_count = int(input("Number of exams to be considered in recent: "))
    
    #Fetches subject list of student
    if series == "":
        query = "select distinct subjects.name, subjects.sid from subjects, results where results.rollno={} and results.sid=subjects.sid order by sid".format(rollno)
    else:
        query = "select distinct subjects.name, subjects.sid from subjects, results, exams where results.rollno={} and results.sid=subjects.sid and results.eid = exams.eid and exams.series_id='{}' order by sid".format(rollno, series)

    cfg.cur.execute(query)
    subject_list = cfg.cur.fetchall()

    #Creates table to display the results
    table = Table()

    table.add_column("Subject", style="green4")
    table.add_column("Average Percentage", style="spring_green3", justify="right")
    table.add_column("Percentage Standard Deviation", style="gold3", justify="right")
    table.add_column("Recent Average Percentage", style="light_sea_green", justify="right")
    table.add_column("Recent Percentage Standard Deviation", style="magenta", justify="right")

    #Adds a row for each subject
    for sub in subject_list:
        #--Uses queries to fetch average and standard deviation of percentages for each subject and total
        #--These are complicated by the fact that when total percentages are being calculated, it needs to be divided by the number of subjects
        if series == "":
            query = "select avg(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from results, exams, (select eid, count(*) as c from exam_subjects group by eid) as num where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.eid=num.eid".format(sub[1], rollno) #type: ignore
        else:
            query = "select avg(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from results, exams, (select eid, count(*) as c from exam_subjects group by eid) as num where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.series_id='{2}'".format(sub[1], rollno, series) #type: ignore
        cfg.cur.execute(query)
        overall_data = cfg.cur.fetchall()

        #--Same as above, but only for recent exams
        if series == "":
            query = "select avg(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from (select results.marks, exams.sub_max_marks, row_number() over (order by date) row_num from results, exams where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid) as n, (select eid, count(*) as c from exam_subjects group by eid) as num where row_num <= {2};".format(sub[1], rollno, recent_count) #type: ignore
        else:
            query = "select avg(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from (select results.marks, exams.sub_max_marks, row_number() over (order by date) row_num from results, exams where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.series_id='{3}') as n, (select eid, count(*) as c from exam_subjects group by eid) as num where row_num <= {2};".format(sub[1], rollno, recent_count, series) #type: ignore
        cfg.cur.execute(query)
        recent_data = cfg.cur.fetchall()
        
        table.add_row(sub[0], str(int(100*overall_data[0][0]) / 100), str(int(100*overall_data[0][1]) / 100), str(int(100*recent_data[0][0]) / 100), str(int(100*recent_data[0][1]) / 100)) #type: ignore

    #Displays the result
    print(table)


def _update_password(rollno):
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

def _delete_account(rollno):
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


