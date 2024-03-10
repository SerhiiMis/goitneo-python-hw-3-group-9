from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class AddressBook(UserDict): # клас, який містить методи для додавання, пошуку, видалення контактів. А також отримання днів народження на наступному тижні
    def add_record(self, record):
        self.data[record.name.value] = record

    def search_record(self, name):
        return self.data.get(name)

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_birthdays_per_week(self):
        birthdays_per_week = defaultdict(list)
        today = datetime.today().date()
        for record in self.values():
            if record.birthday:
                birthday_this_year = datetime.strptime(record.birthday.value, '%d.%m.%Y').date().replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                delta_days = (birthday_this_year - today).days
                if 0 <= delta_days <= 7:  
                    birthday_day_of_week = (today + timedelta(days=delta_days)).strftime("%A")
                    if birthday_day_of_week in ["Saturday", "Sunday"]:
                        birthday_day_of_week = "Monday"
                    birthdays_per_week[birthday_day_of_week].append(record.name.value)

        result = {}
        for day, names in birthdays_per_week.items():
            result[day] = ", ".join(names)
        return result

class Field: # батьківський клас
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field): # клас для створення імені контакт
    def __init__(self, value):
        super().__init__(value)

class Phone(Field): # клас для створення номера телефона контакта
    def __init__(self, value):
        super().__init__(value)
        self.validate_phone(value)

    def validate_phone(self, phone): # валідація номера телефона
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Invalid phone number format. Please enter a 10-digit number.")

class Birthday(Field): # клас для створення дня народження контакта
    def __init__(self, value):
        super().__init__(value)
        self.validate_birthday(value)

    def validate_birthday(self, birthday): # валідація формату дня народження
        try:
            datetime.strptime(birthday, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid birthday format. Please use DD-MM-YYYY.")

class Record: # клас, який представляє контакт і його методи
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone else []
        self.birthday = Birthday(birthday) if birthday else None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'Not set'}"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                del self.phones[i]
                break

    def edit_phone(self, old_phone, new_phone):
        for i in range(len(self.phones)):
            if self.phones[i].value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    def search_phone(self, phone):
        return any(p.value == phone for p in self.phones)

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday already exists.")
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return str(self.birthday)
        return "Birthday not set."

    def delete_birthday(self):
        self.birthday = None

def input_error(func): # декоратор, який обробляє помилки вводу
    def inner(*args, **kwargs):
        if len(args) == 0:  
            return func(*args, **kwargs)
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command syntax."
    return inner

@input_error
def add_contact(args, address_book):
    if len(args) != 2:
        raise ValueError("Give me name and phone please.")
    name, phone = args
    record = Record(name, phone)
    address_book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, address_book):
    if len(args) != 2:
        raise ValueError("Give me name and new phone please.")
    name, new_phone = args
    record = address_book.search_record(name)
    if record:
        record.edit_phone(record.phones[0].value, new_phone)
        return "Contact updated."
    else:
        raise KeyError("Contact not found.")

@input_error
def show_phone(args, address_book):
    if len(args) != 1:
        raise ValueError("Give me name please.")
    name = args[0]
    record = address_book.search_record(name)
    if record:
        return ', '.join(p.value for p in record.phones)
    else:
        raise KeyError("Contact not found.")

@input_error
def show_all(args, address_book):
    if len(args) != 0:
        raise ValueError("Invalid command syntax.")
    if address_book:
        return "\n".join(str(record) for record in address_book.values())
    else:
        return "No contacts saved."

@input_error
def add_birthday(args, address_book):
    if len(args) != 2:
        raise ValueError("Give me name and birthday please.")
    name, birthday = args
    record = address_book.search_record(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added to the contact."
    else:
        raise KeyError("Contact not found.")

@input_error
def show_birthday(args, address_book):
    if len(args) != 1:
        raise ValueError("Give me name please.")
    name = args[0]
    record = address_book.search_record(name)
    if record:
        return record.show_birthday()
    else:
        raise KeyError("Contact not found.")

@input_error
def birthdays(args, address_book):
    if len(args) != 0:
        raise ValueError("Invalid command syntax.")
    upcoming_birthdays = address_book.get_birthdays_per_week()
    if upcoming_birthdays:
        result = []
        for day, names in upcoming_birthdays.items():
            result.append(f"{day}: {names}")
        return "\n".join(result)
    else:
        return "No upcoming birthdays."

def parse_input(user_input): # функція розбирає рядок введення користувача на команду та аргументи
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def main(): # головна функція програми
    address_book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command == "change":
            print(change_contact(args, address_book))
        elif command == "phone":
            print(show_phone(args, address_book))
        elif command == "all":
            print(show_all(args, address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(args, address_book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()