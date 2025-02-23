import pickle
import re
from datetime import datetime
from collections import UserDict
from abc import ABC, abstractmethod

# Abstract base class for Views
class AbstractView(ABC):
    
    @abstractmethod
    def display(self, message):
        pass
    
    @abstractmethod
    def prompt(self, message):
        pass

# Console-specific implementation of the view
class ConsoleView(AbstractView):
    
    def display(self, message):
        print(message)
    
    def prompt(self, message):
        return input(message)

# Model classes
class Field:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))
    
    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]
    
    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = Phone(new_number).value
                return
        raise ValueError("Phone number not found.")
    
    def add_birthday(self, date):
        self.birthday = Birthday(date)
    
    def show_birthday(self):
        return f"Birthday of {self.name}: {self.birthday}" if self.birthday else "No birthday set"
    
    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

# Serialization functions
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# Controller class
class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def add_contact(self):
        name = self.view.prompt("Enter contact name: ")
        phone = self.view.prompt("Enter phone number: ")
        record = self.model.find(name)
        if not record:
            record = Record(name)
            self.model.add_record(record)
        record.add_phone(phone)
        self.view.display("Contact added successfully.")
    
    def list_contacts(self):
        self.view.display(self.model if self.model.data else "No contacts found.")
    
    def show_help(self):
        self.view.display("""
Available commands:
  add - Add a new contact
  list - List all contacts
  help - Show this help message
  exit - Exit the program
""")

# Main application
class Main:
    def __init__(self):
        self.model = load_data()
        self.view = ConsoleView()
        self.controller = Controller(self.model, self.view)
    
    def run(self):
        self.view.display("Welcome to Personal Assistant!")
        while True:
            command = self.view.prompt("Enter command: ")
            if command == "add":
                self.controller.add_contact()
            elif command == "list":
                self.controller.list_contacts()
            elif command == "help":
                self.controller.show_help()
            elif command == "exit":
                save_data(self.model)
                self.view.display("Goodbye!")
                break
            else:
                self.view.display("Unknown command. Type 'help' for options.")

if __name__ == "__main__":
    app = Main()
    app.run()


   

