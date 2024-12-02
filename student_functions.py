from os import system
from rich import print
from rich.prompt import Confirm
from rich.table import Table
from mysql.connector import IntegrityError
from datetime import datetime
import config
import pwinput
import numpy

def student_auth():
    while True:
        system('cls')
        print("-" * 32)
        print("[violet]Student Authentication")
        print("-" * 32)

        print("\n")
        print("1. Return to Home Screen")
        print("2. Login")
        print("3. Sign up")

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
            print("[red]Invalid Input")
        except config.LoginError:
            pass
        except KeyboardInterrupt:
            print("[red]Cancelled operation")
            pass

        config.wait_for_enter()

def _login():
    print("\n")
    rollno = input("Enter your roll number: ")
    pwd = pwinput.pwinput("Enter your password (contact admin if you forgot): ")

    config.cur.execute("select pwd, name from students where rollno = '{}';".format(rollno))
    users = config.cur.fetchall()

    if len(users) == 0 or users[0][0] != pwd: # type: ignore
        print("[red]Incorrect roll number or password")
        raise config.LoginError

    print("[green]Logged in successfully!")

    _student_home(rollno, users[0][1]) # type: ignore

def _signup():
    print("\n")

    rollno = int(input("Enter your roll number: "))
    name = input("Enter your name: ")
    pwd = pwinput.pwinput("Enter a password: ")

    re_pwd = pwinput.pwinput("Confirm your password: ")

    if pwd != re_pwd:
        print("[red]Could not create profile")
        print("[red]Password and confirmed password do not match")
        return

    try:
        config.cur.execute("insert into students values({}, '{}', '{}')".format(rollno, name, pwd))
        config.con.commit()
    except IntegrityError:
        print("[red]Roll number taken")
        print("[red]Could not create profile")
    except:
        print("[red]Could not create profile")
    else:
        print("[green]Profile created successfully!")


def _student_home(rollno, name):
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
            print("[red]Invalid Input")
        except config.AccountDeleted:
            break
        except KeyboardInterrupt:
            print("[red]Cancelled operation")
            pass

        config.wait_for_enter()    


def _view_student_results(rollno):
    print("\n")

    series = input("Series (leave blank to display all): ")

    if series == "":
        query = "select results.eid, exams.date, exams.series_id, results.marks, results.ranking, exams.sub_max_marks from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid order by exams.date desc".format(rollno)
    else:
        query = "select results.eid, exams.date, exams.series_id, results.marks, results.ranking, exams.sub_max_marks from results, exams where results.sid = '000' and results.rollno = {} and results.eid = exams.eid and exams.series_id = '{}' order by exams.date desc".format(rollno, series)

    try:
        config.cur.execute(query)
        exam_list = config.cur.fetchall()
        if len(exam_list) == 0:
            print("[red]No results found")
            raise
    except:
        print("[red]Error: Could not fetch results")
        return

    # Display the result

    table = Table()

    table.add_column("Exam ID", style="cyan", no_wrap=True)
    table.add_column("Date", style="deep_pink4")
    table.add_column("Series", style="spring_green3")
    table.add_column("Marks", style="magenta", justify="right")
    table.add_column("Percentage", style="gold3", justify="right")
    table.add_column("Rank", style="light_sea_green", justify="right")
    table.add_column("Subjects")

    for exam in exam_list:        
        try:
            config.cur.execute("select exam_subjects.sid, subjects.name from exam_subjects, subjects where eid='{}' and exam_subjects.sid = subjects.sid order by exam_subjects.sid;".format(exam[0])) #type: ignore
            sub_details = config.cur.fetchall()
        except:
            print("[red]Error: Could not display result")
            return


        sub_table = Table(expand=True, padding=(0, 4), box=None)
        sub_table.add_column("Subject", style="green4")
        sub_table.add_column("Marks", style="turquoise2", justify="right")
        sub_table.add_column("Percentage", style="blue_violet", justify="right")
        sub_table.add_column("Rank", style="chartreuse3", justify="right")

        for sub in sub_details:
            config.cur.execute("select marks, ranking from results where rollno={} and eid ='{}' and sid='{}'".format(rollno, exam[0], sub[0])) #type: ignore
            sub_results = config.cur.fetchall()[0]
            sub_table.add_row(
                sub[1],                                                         # type: ignore
                str(sub_results[0]),                                            # type: ignore
                str(int(10000 * sub_results[0] / exam[5]) / 100),         # type: ignore
                str(sub_results[1] if not sub_results[1] is None else "-")      # type: ignore
            ) 

        table.add_row(
            exam[0],                                                            # type: ignore
            datetime.strftime(exam[1], '%Y-%m-%d'),                             # type: ignore
            exam[2],                                                            # type: ignore
            str(exam[3]),                                                       # type: ignore
            str(int(10000 * exam[3] / (len(sub_details) * exam[5])) / 100),     # type: ignore
            str(exam[4] if not exam[4] is None else "-"),                       # type: ignore
            sub_table
        )

    print(table)

def _view_analysis(rollno):
    print("\n")

    series = input("Series (leave blank to use all): ")

    recent_count = int(input("Number of exams to be considered in recent: "))
    
    if series == "":
        query = "select distinct subjects.name, subjects.sid from subjects, results where results.rollno={} and results.sid=subjects.sid order by sid".format(rollno)
    else:
        query = "select distinct subjects.name, subjects.sid from subjects, results, exams where results.rollno={} and results.sid=subjects.sid and results.eid = exams.eid and exams.series_id='{}' order by sid".format(rollno, series)

    config.cur.execute(query)
    subject_list = config.cur.fetchall()

    table = Table()

    table.add_column("Subject", style="green4")
    table.add_column("Average Percentage", style="spring_green3", justify="right")
    table.add_column("Percentage Standard Deviation", style="gold3", justify="right")
    table.add_column("Recent Average Percentage", style="light_sea_green", justify="right")
    table.add_column("Recent Percentage Standard Deviation", style="magenta", justify="right")

    for sub in subject_list:
        # The queries are very complicated, do not attempt to alter them unless you are prepared to spend hours on it
        if series == "":
            query = "select avg(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from results, exams, (select eid, count(*) as c from exam_subjects group by eid) as num where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.eid=num.eid".format(sub[1], rollno) #type: ignore
        else:
            query = "select avg(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * results.marks / exams.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from results, exams, (select eid, count(*) as c from exam_subjects group by eid) as num where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.series_id='{2}'".format(sub[1], rollno, series) #type: ignore
        config.cur.execute(query)
        overall_data = config.cur.fetchall()

        if series == "":
            query = "select avg(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from (select results.marks, exams.sub_max_marks, row_number() over (order by date) row_num from results, exams where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid) as n, (select eid, count(*) as c from exam_subjects group by eid) as num where row_num <= {2};".format(sub[1], rollno, recent_count) #type: ignore
        else:
            query = "select avg(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end), stddev_pop(100 * n.marks / n.sub_max_marks / case when '{0}'='000' then num.c else 1 end) from (select results.marks, exams.sub_max_marks, row_number() over (order by date) row_num from results, exams where results.rollno={1} and results.sid='{0}' and exams.eid=results.eid and exams.series_id='{3}') as n, (select eid, count(*) as c from exam_subjects group by eid) as num where row_num <= {2};".format(sub[1], rollno, recent_count, series) #type: ignore
        config.cur.execute(query)
        recent_data = config.cur.fetchall()
        

        table.add_row(sub[0], str(int(100*overall_data[0][0]) / 100), str(int(100*overall_data[0][1]) / 100), str(int(100*recent_data[0][0]) / 100), str(int(100*recent_data[0][1]) / 100)) #type: ignore

    print(table)


def _update_password(rollno):
    print("\n")

    pwd = pwinput.pwinput("Please enter current password: ")
    
    config.cur.execute("select pwd from students where rollno = {}".format(rollno))

    if pwd != config.cur.fetchall()[0][0]: # type: ignore
        print("[red]Incorrect password")
        return
    
    new_pwd = pwinput.pwinput("Enter new password: ")
    re_new_pwd = pwinput.pwinput("Confirm new password: ")


    if new_pwd != re_new_pwd:
        print("[red]Did not update passsword")
        print("[red]Password and confirmed password do not match")
        return
    
    config.cur.execute("update students set pwd='{}' where rollno={}".format(new_pwd, rollno))
    config.con.commit()

    print("[green]Password updated successfully")

def _delete_account(rollno):
    print("\n")

    print("[red bold]This action is irreversible")
    confirmed = Confirm.ask("[blue bold]Are you sure you wish to delete your profile?")

    if not confirmed:
        return
    
    pwd = pwinput.pwinput("Please enter password for verification: ")
    
    config.cur.execute("select pwd from students where rollno = {}".format(rollno))

    if pwd != config.cur.fetchall()[0][0]: # type: ignore
        print("[red]Incorrect password")
        return
    
    config.cur.execute("delete from students where rollno={}".format(rollno))
    config.con.commit()

    print("[green]Profile deleted successfully")

    config.wait_for_enter()

    raise config.AccountDeleted

