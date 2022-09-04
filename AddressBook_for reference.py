from collections import UserDict
from datetime import datetime
import re
import shelve


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Can't find the record"
    return inner


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):

    @Field.value.setter
    def value(self, name):
        if re.match (r"[a-zA-Z]+", name):
            self._value = name
        else:
            raise ValueError

    def __repr__(self):
        return f'{self._value}'


class Phone(Field):

    @Field.value.setter
    def value(self, phone):
        if re.match (r"^\+\d{11}\d?", phone):
            self._value = phone
        else:
            raise ValueError

    def __repr__(self):
        return f'{self._value}'


class Birthday(Field):

    @Field.value.setter
    def value(self, value):
        if value:
            try:
                birthday = datetime.strptime(value, "%Y/%m/%d").date()
                self._value = birthday
            except TypeError or ValueError:
                raise ValueError
        else:
            self._value = ""

    def __repr__(self):
        return f'{self._value}'


class Record(UserDict):

    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday

    def __repr__(self):
        if self.birthday:
            return f'{self.name.value}: {[p.value for p in self.phones]}, DOB {self.birthday}'
        return f'{self.name.value}: {[p.value for p in self.phones]}'

    def add_phone(self, phone: Phone):
        if phone._value not in [p._value for p in self.phones]:
            self.phones.append(phone)
            return phone

    def delete_phone(self, phone: Phone):
        for p in self.phones:
            if p._value == phone._value:
                self.phones.remove(p)
                return phone

    def change_phone(self, phone: Phone, new_phone: Phone):
        if self.delete_phone(phone):
            self.add_phone(new_phone)
            return phone, new_phone

    def days_to_birthday(self):
        delta1 = datetime(datetime.now().year, self.birthday._value.month, self.birthday._value.day)
        delta2 = datetime(datetime.now().year + 1, self.birthday._value.month, self.birthday._value.day)
        result = ((delta1 if delta1 > datetime.now() else delta2) - datetime.now()).days
        return f'Birthday is in {result} days.'


class AddressBook(UserDict):

    def iterator(self, num: int = 2):
        data = self.data
        items = list(data.items())
        counter = 0
        result = ''
        for i in items:
            result += f'{i}'
            counter += 1
            if counter >= num:
                yield result
                result = ''
                counter = 0
        yield result

    def __repr__(self):
        return f'{self.data}'

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def save_to_file(self):
        with shelve.open('address_book') as ab:
            ab['contacts'] = self.data



def func_hello(*args, **kwargs):
    return "How can I help you?"


def add_contact(name, phone=None, birthday=None):
    name_a = Name(name)
    phone_a = Phone(phone[0]) if phone else None
    birthday_a = Birthday(birthday)
    record_new = Record(name_a, phone_a, birthday_a)
    record_lookup = contacts_dict.get(name)
    if isinstance(record_lookup, Record):
        if phone:
            record_lookup.add_phone(Phone(phone[0]))
            return f'New phone number added for {name.capitalize()}'
        if birthday:
            record_lookup.birthday = birthday
            return f'Birthday information updated for {name.capitalize()}'
    contacts_dict.add_record(record_new)
    contacts_dict.save_to_file()
    return f'Information record for {name.capitalize()} added'


@input_error
def change_contact(name, phone: list, *args, **kwargs):
    record = contacts_dict.get(name)
    if isinstance(record, Record):
        for p in record.phones:
            if str(p) == phone[0]:
                record.change_phone(Phone(phone[0]), Phone(phone[1]))
                return f'Contact {name.capitalize()} changed number {phone[0]} to number {phone[1]}'
        return f'Contact {name.capitalize()} has no number {phone[0]} on file. Number was not changed.'
    contacts_dict.save_to_file()
    return f'Sorry, phone book has no entry with name {name}'


@input_error
def phone_contact(name, *args, **kwargs):
    return f"{name.capitalize()}'s numbers are {contacts_dict[name].phones}"


@input_error
def birthday_contact(name, *args, **kwargs):
    record_lookup = contacts_dict.get(name)
    if isinstance(record_lookup, Record):
        if record_lookup.birthday._value is None:
            return "No birthday data available"
        else:
            result_bd = record_lookup.days_to_birthday()
            return f"{name.capitalize()}'s birthday is {contacts_dict[name].birthday}. {result_bd}"
    return "No personal record available"


def show_all(*args, **kwargs):
    result_iter = contacts_dict.iterator(2)
    result = ""
    for i in result_iter:
        result += f'{i}\n'
    return result.strip()


def func_exit(*args, **kwargs):
    contacts_dict.save_to_file()
    return 'Address book saved to file.\nGood bye!'


def func_search(*args, **kwargs):
    search_input = input('Please, enter part of the name (lowercase) or phone number:')
    with shelve.open('address_book') as ab:
        data: UserDict = ab['contacts']
        search_output = []
        for value in data.values():
            if search_input in str(value.name):
                search_output.append(value)
            for p in value.phones:
                if search_input in str(p):
                    search_output.append(value)
        return search_output


"""Парсер команд. Часть которая отвечает за разбор введенных пользователем строк,
выделение из строки ключевых слов и модификаторов команд."""


def input_error_norm(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return 'Please enter full command'
    return inner


@input_error_norm
def normalize(raw_user_input: str) -> dict:
    user_input = raw_user_input.lower().strip()
    user_command: dict = {'command': None, 'name': None, 'phone': [], 'birthday': None}

    if user_input in ['hello', 'show all', 'good buy', 'close', 'exit', 'search']:
        user_command['command'] = user_input
    else:
        user_input_list = user_input.split()
        user_command['command'] = user_input_list[0]
        user_command['name'] = user_input_list[1]
        if len(user_input_list) > 2:
            if "/" in user_input_list[2]:
                user_command['birthday'] = user_input_list[2]
            else:
                user_command['phone'].append(user_input_list[2])
        if len(user_input_list) > 3:
            user_command['phone'].append(user_input_list[3])

    return user_command


def input_error_main(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return 'Please, check the data format:\n- name should be latin letters only;\n- phone should be in format + /country code/ /area code/ /phone number/;\n- date of birth should be in format yyyy/mm/dd.'
        except TypeError:
            return 'Please enter full command'
    return inner


COMMANDS = {func_hello: 'hello', show_all: 'show all', add_contact: 'add', change_contact: 'change',
            phone_contact: 'phone', birthday_contact: 'birthday', func_exit: ['good buy', 'close', 'exit'], func_search: 'search'}


@input_error_main
def output_func(user_command):
    command = user_command['command']
    name_command = user_command['name']
#    phone_command = None if (user_command['phone'] == []) else user_command['phone']
    phone_command = user_command['phone']
    birthday_command = user_command['birthday']
    for k, v in COMMANDS.items():
        if command in v:
            return k(name=name_command, phone=phone_command, birthday=birthday_command)   # name_command, *phone_command, birthday_command



# contacts_dict = AddressBook()#
# with shelve.open('address_book') as ab:
#     contacts_dict.update(dict(ab['contacts']))


def main():

    print('Address book\nCommands:\nadd name phone DOB\nchange name old_phone new_phone\nshow all\nbirthday name\nphone name\nsearch')
    while True:
        user_input = input('>>>')
        user_command = normalize(user_input)
        result = output_func(user_command)
        print(result)
        if result == 'Good bye!':
            break


if __name__ == "__main__":
    main()
