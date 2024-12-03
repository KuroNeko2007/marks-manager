from os import system
from rich import print

import cfg
from admin_functions import admin_auth
from student_functions import student_auth

#TODO Ensure every error report starts with error
#TODO Handle keyboard interrupt with newline
#TODO Add exaclamtion in all success

def home_page():
    while True:
        system('cls')
        print("-" * 32)
        print("[bold violet]Welcome to the Marks Manager")
        print("-" * 32)
        
        print("\n")
        print("1. Exit")
        print("2. Admin")
        print("3. Student")
        print()


        try:
            choice = int(input("Enter your choice: "))
            if choice == 1:
                print("[blue]Exiting...")
                break
            elif choice == 2:
                admin_auth()
                continue
            elif choice == 3:
                student_auth()
                continue
            else:
                raise ValueError
        except ValueError:
            cfg.failure("Invalid Input")
        except Exception as e:
            # DEBUG
            cfg.failure("[bold]Unhandled error: ")
            print(e)
            cfg.wait_for_enter("Press enter to exit...")
            break

        cfg.wait_for_enter()


if __name__ == "__main__":
    try:
        cfg.connect()
    except:
        system('cls')
        cfg.failure("[bold]Could not connect to database")
        cfg.wait_for_enter("Press enter to exit...")
    else:
        home_page()

        cfg.cur.close()
        cfg.con.close()