from admin_functions import admin_auth
from student_functions import student_auth
from os import system
from rich import print
import config

#TODO Ensure every error report starts with error
#TODO Handle keyboard interrupt with newline
#TODO Add exaclamtion in all success

def home_page():
    while True:
        system('cls')
        print("-" * 32)
        print("[bold violet]Welcome to the Marks Analyser")
        print("-" * 32)
        
        print("\n")
        print("1. Exit")
        print("2. Admin")
        print("3. Student")

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
            print("[red]Invalid Input")
        except Exception as e:
            print("[red bold]Unhandled error: ", e)
            config.wait_for_enter("Press enter to exit...")
            break

        config.wait_for_enter()


if __name__ == "__main__":
    try:
        config.connect()
    except:
        system('cls')
        print("[bold red]Could not connect to database")
        config.wait_for_enter("Press enter to exit...")
    else:
        home_page()

        config.cur.close()
        config.con.close()