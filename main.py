import csv
import logging
import os
import platform
import re
import sys

from fuzzywuzzy import fuzz, process
import readline


commands = {}


def set_commands(name, *additional):
    def inner(func):
        commands[name] = func
        for command in additional:
            commands[command] = func
    return inner


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Enter all require arguments please.\nTo see more info type 'help'."
    inner.__doc__ = func.__doc__
    return inner


def open_file_and_check_name(name: str) -> tuple:
    """Take as input username. Return tuple with 
     dictionary in which key is the name and value is the phone number 
    and bool value True if name already exist in dataframe, False otherwise."""
    try:
        with open("data.csv") as file:
            reader = csv.DictReader(file)
            data = {}
            for row in reader:
                username = row["Name"]
                phone = row["Phone number"]
                data[username] = phone

    except FileNotFoundError:
        data = {}

    name_exists = bool(data.get(name))

    return (data, name_exists)


def write_to_csv(data: dict, file_path: str):
    fieldnames = ["Name", "Phone number"]

    with open(file_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for name, phone in data.items():
            writer.writerow({"Name": name, "Phone number": phone})


@set_commands("add")
@input_error
def add(*args):
    """Take as input username and phone number and add them to the base."""
    name = args[0]
    phone_number = args[1]

    data, name_exists = open_file_and_check_name(name)

    if name_exists:
        return f"Name {name} already exists."\
            "If you want to change it, please type 'change <name> <phone number>'."
    else:
        data[name] = phone_number

    write_to_csv(data, "data.csv")
    return f"User {name} added successfully."


@set_commands("change")
@input_error
def change(*args):
    """Take as input username and phone number and changes the corresponding data."""
    name = args[0]
    phone_number = str(args[1])

    data, name_exists = open_file_and_check_name(name)

    if not name_exists:
        return f"Name {name} doesn`t exists."\
            "If you want to add it, please type 'add <name> <phone number>'."
    else:
        data[name] = phone_number

    write_to_csv(data, "data.csv")
    return f"Phone number for {name} has been updated."


@set_commands("clear")
@input_error
def clear(*args):
    """Clear the console."""
    system = platform.system()
    if system == "Windows":
        os.system("cls")
    elif system in ("Linux", "Darwin"):
        os.system("clear")
    else:
        return "Sorry, this command is not available on your operating system."


@set_commands("hello")
@input_error
def hello(*args):
    """Greet user."""
    return "How can I help you?"


@set_commands("help")
@input_error
def help_command(*args):
    """Show all commands available."""
    all_commands = ""
    for command, func in commands.items():
        all_commands += f"{command}: {func.__doc__}\n"
    return all_commands


@set_commands("phone")
@input_error
def phone(*args):
    """Take as input username and show user`s phone number."""
    name = args[0]

    data, name_exists = open_file_and_check_name(name)

    if not name_exists:
        return f"Name {name} doesn`t exists. "\
            "If you want to add it, please type 'add <name> <phone number>'."
    else:
        phone_number = data[name]
        return f"Phone number for {name}: {phone_number}."


@set_commands("show all")
@input_error
def show_all(*args):
    """Show all users."""
    try:
        with open("data.csv") as file:
            reader = csv.DictReader(file)
            data = {}
            for row in reader:
                username = row["Name"]
                phone = row["Phone number"]
                data[username] = phone

    except FileNotFoundError:
        data = {}

    all_users = ""
    for name, phone in data.items():
        all_users += f"{name}: {phone}\n"
    return all_users


@set_commands("exit", "close", "good bye")
@input_error
def exit(*args):
    """Interrupt program."""
    sys.exit(0)


def completer(text, state):
    if not text.isalpha():
        return None
    options = [cmd for cmd in commands.keys() if cmd.startswith(text.lower())]
    if not options:
        return None
    if state < len(options):
        return options[state]
    return None


def parse_command(user_input: str):
    match = re.search(r"^show\s|^good\s", user_input.lower())
    try:
        if match:
            user_command = " ".join(user_input.split()[:2]).lower()
            command_arguments = user_input.split()[2:]
        else:
            user_command = user_input.split()[0].lower()
            command_arguments = user_input.split()[1:]
    except IndexError:
        return "Please enter a command name."

    if user_command not in commands.keys():
        logging.basicConfig(level=logging.ERROR)
        best_match, match_ratio = process.extractOne(user_command,
                                                     commands.keys(),
                                                     scorer=fuzz.partial_ratio)
        if match_ratio >= 60:
            return f"Command not found.\nPerhaps you meant '{best_match}'."
        else:
            return "Command not found.\nTo view all available commands, enter 'help'."
    else:
        return commands[user_command](*command_arguments)


def main():
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        user_input = input("Enter command: ")
        result = parse_command(user_input)

        if result:
            print(result)


if __name__ == "__main__":
    main()
