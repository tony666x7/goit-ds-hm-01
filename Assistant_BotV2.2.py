from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Номер має містити лише 10 цифр.")
        super().__init__(value)
    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте формат DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        if phone in self.phones:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if str(phone) == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone_number):
        for phone in self.phones:
            if str(phone) == phone_number:
                return phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Ім'я контакту: {self.name.value}, Номер: {'; '.join(str(p) for p in self.phones)}, День Народження: {self.birthday}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        if name in self.data:
            return self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                # Витягуємо день народження з об'єкта Birthday
                birthday = record.birthday.value.replace(year=today.year)
                # Якщо день народження вже минув у поточному році, додаємо рік
                if birthday < today:
                    birthday = birthday.replace(year=today.year + 1)
                # Перевіряємо, чи день народження потрапляє в наступний тиждень
                if today <= birthday <= next_week:
                    upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays


def save_data(book, filename="addressbook.pk1"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pk1"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook() # Повернення нової адресної книги, якщо файл не знайдено або порожній

def input_error(func):
    # Декоратор для обробки ValueError до додавання номеру
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Будь ласка, введіть коректні дані.\n\
            В форматі \"Команда\" \"Ім'я\" \"Номер(має містити 10 цифр)\"\n"
        
    return inner

def input_error2(func):
    # Декоратор для обробки ValueError до зміни номеру
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Будь ласка, введіть коректні дані.\n\
            В форматі \"Команда\" \"Ім'я\" \"Новий номер(має містити 10 цифр)\"\n"
        
    return inner

def input_error3(func):
    # Декоратор для обробки ValueError до додавання Дня народження
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Будь ласка, введіть коректні дані.\n\
            В форматі \"Команда\" \"Ім'я\" \"Дата народження у форматі DD.MM.YYYY\"\n"
        
    return inner

def handle_error(func):
    # Декоратор для обробки помилок KeyError, ValueError
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт не існує.\
            Будь ласка, введіть існуючий контакт.\n"
        except ValueError:
            return "Контакт не існує.\
            Будь ласка, введіть існуючий контакт.\n"

    return wrapper

def parse_input(user_input):
    # Функція для розбору введеного користувачем рядка на команду та аргументи
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    # Додає контакт
    name, phone = args
    if name in book.data:
        return f"Контакт з ім'ям {name} вже існує.\n"
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Контакт {name} додано\n"
    
@input_error2   
def change_contact(args, book):
    # Змінює номер телефону для існуючого контакту
    name, phone = args
    if name in book.data:
        record = book.find(name)
        record.phones.clear()
        record.add_phone(phone)
        return f"Контакт {name} змінено\n"
    else:
        return f"Контакт {name} не знайдено\n"

@handle_error
def show_phone(args, book):
    # Виводить ім'я на номер збереженого контакту
    name, = args
    record = book.find(name)
    if record:
        if record.phones:
            return f"Телефонний номер для {name}: {', '.join(str(phone) for phone in record.phones)}\n"
        else:
            return f"Для контакту {name} не вказано телефонного номера.\n"
    else:
        return f"Контакт {name} не знайдено.\n"

def show_contact(book):
    # Виводить усі збережені контакти
    if book.data:
        result = "Всі збережені контакти: \n"
        for record in book.data.values():     
            result += str(record) + "\n"
        return result
    else:
        return "Немає збережених контактів\n"

@handle_error    
def delete_contact(args, book):
    # Видаляє вказанний контакт
    name, = args
    book.delete(name)
    return f"Контакт {name} видалено\n"

@input_error3
def add_birthday(args, book):
    # Додає День Народження
    name, birthday = args
    if name in book.data:
        record = book.find(name)
        record.add_birthday(birthday)
        return f"День народження для {name} додано\n"
    else:
        return f"Контакт {name} не знайдено\n"

@handle_error
def show_birthday(args, book):
    # Виводить ім'я та дату народження контакту 
    name, = args
    if name in book.data:
        record = book.find(name)
        if record.birthday:
            return f"День народження {name}: {record.birthday}\n"
        else:
            return f"День народження для {name} не вказано\n"
    else:
        return f"Контакт {name} не знайдено\n"

@handle_error
def birthdays(args, book):
    #  Виводить ім'я та дату народження контакту якщо його день народження припадає на наступний тиждень 
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return f"Користувачі, яких потрібно привітати на наступному тижні: {', '.join(upcoming_birthdays)}\n"
    else:
        return "На наступному тижні немає днів народження\n"

def main():
    # Основний цикл функції
    
    book = load_data()

    print("\nВітаю! Я віртуальний помічник\n\
    \n\t\t Меню\
    \nКоманда \t\t\t\t-> \t\t\tДія\
    \n\
      \nhello \t\t\t\t\t-> \tПривітання\
    \nadd 'name', 'phone' \t\t\t-> \tДодати контакт до списку\
    \nchange 'name', 'new_phone' \t\t-> \tЗамінити контакт в списку\
    \ndelete 'name' \t\t\t\t-> \tВидалити контакт зі списку\
    \nphone 'name' \t\t\t\t-> \tПоказати телефон для вказаного контакту\
    \nall \t\t\t\t\t-> \tВивести всі збережені контакти\
    \nadd-birthday 'name', 'DD.MM.YYYY' \t-> \tДодати день народження для вказаного контакту\
    \nshow-birthday 'name' \t\t\t-> \tПоказати день народження для вказаного контакту\
    \nbirthdays \t\t\t\t-> \tПоказати дні народження на наступний тиждень\
    \nexit/close \t\t\t\t-> \tЗавершення роботи помічника\n")
    
    while True:
        user_input = None
        command = None
        try:
            user_input = input("Введіть команду: ")
        except EOFError:
            print("Кінець введення. Програма завершує роботу.")
        if user_input is not None:
            command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("До зустрічі!\n")
            break
        elif command == "hello":
            print("Як я можу допомогти?\n")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_contact(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        else:
            print("Невірна команда.\n")

    save_data(book)

if __name__ == "__main__":
    main()