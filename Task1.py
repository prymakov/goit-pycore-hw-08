from collections import UserDict
from datetime import datetime, timedelta
import pickle

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            print("Contact not found.")
        except ValueError as e:
            print(f"Error: {e}")
        except IndexError:
            print("Invalid input. Please provide correct data.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)
        

class Phone(Field):
    def __init__(self, number):
        if self.is_valid_phone(number):
            super().__init__(number)
        else:
            raise ValueError("Invalid phone format. Should be 10 digits")

    @staticmethod
    def is_valid_phone(number):
        return len(number) == 10 and number.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {', '.join(p.value for p in self.phones)}"
        
    def add_birthday(self, date):        
        self.birthday = Birthday(date)

    def add_phone(self, number):        
        self.phones.append(Phone(number))

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None

    def remove_phone(self, number):
        if self.find_phone(number) != None:
            self.phones.remove(self.find_phone(number))
        else:
            print(f"Phone {number} for contact {self.name} not found")
                       
    def edit_phone(self, old_number, new_number):
        for i, p in enumerate(self.phones):
            if p.value == old_number:
                self.phones[i] = Phone(new_number)
                return
        print(f"Phone number {old_number} not found.")

class AddressBook(UserDict):

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"file {filename} тще found. Starting with an empty address book.")
        except Exception as e:
            print(f"An error occurred while loading the address book: {e}")

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"Contact {name} not found.")

    def show_birthday(self, name):
        record = self.find(name)
        if record and record.birthday: 
            print(f"birthday of contact {name} is on {record.birthday}")
        else:
            print(f"contact {record.name} does not have a birthday set")
            
    def birthdays(self):
        current_date = datetime.today()
        birthdays_this_week = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year = current_date.year)

                if birthday_this_year < current_date:
                    birthday_this_year = birthday_this_year.replace(year = current_date.year + 1)

                if current_date <= birthday_this_year < current_date + timedelta(days = 7):
                    birthdays_this_week.append({"name": record.name.value, "congratulation_date": self.get_nearest_workday(birthday_this_year).strftime("%d.%m.%Y")})

        return birthdays_this_week

    def get_nearest_workday(self, date):
        while date.weekday() > 4:
            date = date + timedelta(days=1)
        return date

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)    
    else:
        raise KeyError

@input_error
def show_phones(args, book: AddressBook):
    record = book.find(args[0])
    if record:
        print(f"Phones for {args[0]}: {', '.join(p.value for p in record.phones)}")
    else:
        raise KeyError

@input_error
def show_all_contacts(book: AddressBook):
    for record in book.data.values():
        print(record)

@input_error
def add_birthday(args, book: AddressBook):
    name, date = args
    record = book.find(name)
    if record:
        record.add_birthday(date)
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    book.show_birthday(args[0])

@input_error
def upcoming_birthdays(book):
    birthdays = book.birthdays()
    if birthdays:
        print("\n".join(str(bd) for bd in birthdays))
    else:
        print("no birthdays upcoming week")


def main():
    book = AddressBook()
    filename = "address_book.pkl"
    book.load_from_file(filename)

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_to_file(filename)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            add_contact(args, book)

        elif command == "change":
            change_contact(args, book)

        elif command == "phone":
            show_phones(args, book)
            
        elif command == "all":
            show_all_contacts(book)

        elif command == "add-birthday":
            add_birthday(args, book)

        elif command == "show-birthday":
            show_birthday(args, book)

        elif command == "birthdays":
            upcoming_birthdays(book)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
