import cmd, sys
from turtle import *
import os.path

# Eventually data would be stored in a PostgreSQL database or whatever is decided in class.
USER_PATH = 'users.txt'
cur_user = None
stat_types = []

# Class for the entire user system, handling registration and password/email resets. All currently done through a txt file.
class UserSystem():

    @staticmethod
    def email_exists(email):
        if os.path.isfile(USER_PATH):
            with open(USER_PATH, "r") as fi:
                lines = fi.readlines()
                for line in lines:
                    line = line.strip().split(",")
                    if line:
                        if line[1] == email:
                            return True
        return False

    @staticmethod
    def username_exists(username):
        if os.path.isfile(USER_PATH):
            with open(USER_PATH, "r") as fi:
                lines = fi.readlines()
                for line in lines:
                    line = line.strip().split(",")
                    if line:
                        if line[2] == username:
                            return True
        return False

    @staticmethod
    def password_exists(password):
        if os.path.isfile(USER_PATH):
            with open(USER_PATH, "r") as fi:
                lines = fi.readlines()
                for line in lines:
                    line = line.strip().split(",")
                    if line:
                        if line[3] == password:
                            return True
        
        return False
    
    @staticmethod
    def reset_password(new_password):
        return UserSystem.reset(3, new_password)
    
    @staticmethod
    def reset_email(new_email):
        return UserSystem.reset(1, new_email)
    
    @staticmethod
    def reset_name(new_name):
        return UserSystem.reset(0, new_name)
    
    @staticmethod
    def reset(index, value):
        reset = False
        with open(USER_PATH, "r") as fi:
            lines = fi.readlines()
            for i in range(len(lines)):
                line = lines[i].strip().split(",")
                if line:
                    if line[2] == cur_user:
                        line[index] = value
                        lines[i] = ",".join(line)+"\n"
                        reset = True
        if reset:    
            UserSystem.write_data(lines)
        return reset

    @staticmethod
    def add_user(name, email, username, password):
        with open(USER_PATH, "a+") as fi:
            users = fi.readlines()
            for user in users:
                user = user.split(",")
            fi.write(name+","+email+","+username+","+password+"\n")

    @staticmethod
    def write_data(lines):
        with open(USER_PATH, "w") as fi:
            for line in lines:
                fi.write(line)
    
    @staticmethod
    def delete_current_user():
        deleted = False
        with open(USER_PATH, "r") as fi:
            lines = fi.readlines()
            for i in range(len(lines)):
                line = lines[i].strip().split(",")
                if line:
                    if line[2] == cur_user:
                        lines.pop(i)
                        deleted = True
                        break
        if deleted:    
            UserSystem.write_data(lines)

# Top menu for registering user, login, and quitting application.
class TopShell(cmd.Cmd):
    prompt = "----------- TOP MENU -----------\nCOMMANDS:\n$register\n$login\n$quit\n> "
    
    def do_register(self, arg):
        name = input("Full Name: ")
        email = input("Email: ")
        username = input("Username: ")
        password = input("Password: ")

        if UserSystem.username_exists(username):
            print("Error: Username already registered.")
        elif UserSystem.email_exists(email):
            print("Error: Email already exists")
        else:
            UserSystem.add_user(name, email, username, password)
            print("Success")
    

    def do_login(self, arg):
        global cur_user

        username = input("Username: ")
        password = input("Password: ")

        if not UserSystem.username_exists(username):
            print("Error: Wrong username.")
        elif not UserSystem.password_exists(password):
            print("Error: Wrong password.")
        else:
            print("Success")
            cur_user = username
            try:
                AppShell().cmdloop()
            except Terminator:
                pass

    def do_quit(self, arg):
        exit()

# App menu for once the user is logged into the system.
class AppShell(cmd.Cmd):
    prompt = "----------- APP MENU -----------\nCOMMANDS:\n$profile\n$setup\n$track\n> "

    def do_profile(self, arg):
        try:
            profile_cmd = ProfileShell()
            profile_cmd.cmdloop()
        except Terminator:
            pass
        if profile_cmd.unregistered:
            return self.do_back(arg)

    def do_setup(self, arg):
        try:
            setup_cmd = SetupShell()
            setup_cmd.cmdloop()
        except Terminator:
            pass
    
    def do_track(self, arg):
        try:
            track_cmd = TrackShell()
            track_cmd.cmdloop()
        except Terminator:
            pass

    def do_back(self, arg):
        bye()
        return True


class ProfileShell(cmd.Cmd):
    prompt = "----------- APP PROFILE MENU -----------\nCOMMANDS:\n$password\n$update\n$caregiver\n$upgrade\n$unregister\n> "
    unregistered = False

    def do_password(self, arg):
        new_password = input("New Password: ")

        res = UserSystem.reset_password(new_password)
        if res:
            print("Success")
        else:
            print("Reset operation failed.")
    
    def do_update(self, arg):
        new_email = input("New Email: ")
        new_name = input("New Name: ")

        UserSystem.reset_email(new_email)
        UserSystem.reset_name(new_name)
        print("Success")
    
    def do_unregister(self, arg):
        UserSystem.delete_current_user()
        print("Success")
        self.unregistered = True
        bye()
        return True

    def do_caregiver(self, arg):
        email = input("Caregiver's email: ")

    def do_upgrade(self, arg):
        print("TBD")

    def do_back(self, arg):
        bye()
        return True

# Setup menu to check stats or go back.
class SetupShell(cmd.Cmd):
    prompt = "----------- APP SETUP MENU -----------\nCOMMANDS:\n$stats\n$back\n> "

    def do_stats(self, arg):
        try:
            stats_cmd = StatsShell()
            stats_cmd.cmdloop()
        except Terminator:
            pass


    def do_back(self, arg):
        bye()
        return True

# User will be able to add stats, schedule, and go back. 
class StatsShell(cmd.Cmd):
    prompt = "----------- APP STATS MENU -----------\nCOMMANDS:\n$add\n$schedule\n$back\n> "
    
    def do_add(self, arg):
        tokens = arg.split(";")

        if len(tokens) != 3:
            print("Error: arguments mismatch (3 required)")
        else:
            data_types = tokens[2].split(":")
            if " " in tokens[0]:
                print("Error: space found in first argument.")
            elif len(data_types) % 2 == 1:
                print("Error: Data types pair mismatch.")
            else:
                stat_types.append(tokens[0])
                print("Success")

    def do_schedule(self, arg):
        tokens = arg.split()
        if len(tokens) != 3:
            print("Error: arguments mismatch (3 required)")
        elif tokens[1] != "UMTWRFS" or tokens[2] not in ['am', 'pm']:
            print("Usage: schedule [NAME] UMTWRFS [am/pm]")
        else:
            print("Success")

    def do_back(self, arg):
        bye()
        return True

# User is able to list, record, see report and go back.
class TrackShell(cmd.Cmd):
    prompt = "----------- APP TRACK MENU -----------\nCOMMANDS:\n$list\n$record\n$report\n$back\n> "

    records = []

    def do_list(self, arg):
        print("\n".join(stat_types))

    def do_record(self, arg):
        self.records.append(arg)
        print("records appended")

    def do_report(self, arg):
        print("showing records")
        print("\n".join(self.records))

    def do_back(self, arg):
        bye()
        return True

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))

if __name__ == '__main__':
    TopShell().cmdloop()