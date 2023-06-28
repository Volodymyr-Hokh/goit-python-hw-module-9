import logging
import os
import platform
import sys

from fuzzywuzzy import fuzz, process
import pandas as pd
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


def open_df_and_check_name(name: str) -> tuple:
    """Take as input username. Return tuple with dataframe 
    and bool value True if name already exist in dataframe, False otherwise."""
    try:
        data = pd.read_csv("data.csv")
    except FileNotFoundError:
        data = pd.DataFrame()

    if "Name" in data.columns:
        name_exists = (data["Name"] == name).any()
    else:
        name_exists = False

    return (data, name_exists)


@set_commands("add")
@input_error
def add(*args):
    """Take as input username and phone number and add them to the base."""
    name = args[0]
    phone_number = args[1]

    data, name_exists = open_df_and_check_name(name)

    if name_exists:
        return f"Name {name} already exists."\
            "If you want to change it, please type 'change <name> <phone number>'."
    else:
        new_row = {"Name": name, "Phone number": phone_number}
        data = data._append(new_row, ignore_index=True)

    data.to_csv("data.csv", index=False)
    return f"User {name} added successfully."


@set_commands("change")
@input_error
def change(*args):
    """Take as input username and phone number and changes the corresponding data."""
    name = args[0]
    phone_number = args[1]

    data, name_exists = open_df_and_check_name(name)

    if not name_exists:
        return f"Name {name} doesn`t exists."\
            "If you want to add it, please type 'add <name> <phone number>'."
    else:
        data.loc[data["Name"] == name, "Phone number"] = phone_number

    data.to_csv("data.csv", index=False)
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

    data, name_exists = open_df_and_check_name(name)

    if not name_exists:
        return f"Name {name} doesn`t exists. "\
            "If you want to add it, please type 'add <name> <phone number>'."
    else:
        phone_number = data.loc[data["Name"] == name, "Phone number"].values[0]
        return f"Phone number for {name}: {phone_number}."


@set_commands("showall")
@input_error
def show_all(*args):
    """Show all users."""
    data = pd.read_csv("data.csv")
    all_users = ""
    for _, row in data.iterrows():
        all_users += f"{row['Name']}: {row['Phone number']}\n"
    return all_users


@set_commands("exit", "close", "goodbye")
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
    try:
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
