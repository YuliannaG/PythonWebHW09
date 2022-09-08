import argparse
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

from models import ContactPerson


engine = create_engine("sqlite:///ab.db")
Session = sessionmaker(bind=engine)
session = Session()


def add(*args, **kwargs):
    contact = ContactPerson(**kwargs)
    session.add(contact)
    session.commit()
    return f'Contact {contact.name} added'


def update_contact(*args, **kwargs):
    id = kwargs.pop('id')
    contact = session.get(ContactPerson, id)
    if contact:
        session.execute(update(ContactPerson).
                        where(ContactPerson.id == id).
                        values(**{k: value for k, value in kwargs.items() if value}))
        session.commit()
        return f'Contact with id {contact.id} changed'
    return f'Contact with id - {id} does not exist'


def show_all(*args, **kwargs):
    contacts = session.query(ContactPerson).all()
    return '\n'.join([str(c) for c in contacts])


def remove(*args, **kwargs):
    id = kwargs.get('id')
    contact = session.get(ContactPerson, id)
    if contact:
        session.delete(contact)
        session.commit()
        return f'Contact {contact.name} removed'
    return f'Contact with id - {id} does not exist'


COMMANDS = {show_all: 'show_all', add: 'add',
            update_contact: 'update', remove: 'remove'}


def main():
    parser = argparse.ArgumentParser(description='AddressBook APP')
    parser.add_argument(
        '--command', help='Command: show_all, add, update, remove + id')
    parser.add_argument('--name')
    parser.add_argument('--cell_phone')
    parser.add_argument('--email')
    parser.add_argument('--address')
    parser.add_argument('--id')

    arguments = parser.parse_args()
    # print(arguments)
    my_arg = vars(arguments)
    # print(my_arg)

    command = my_arg.pop('command')
    # _id = my_arg.get('id')
    # name = my_arg.get('name')
    # phone = my_arg.get('phone')
    # email = my_arg.get('email')
    # address = my_arg.get('address')
    for k, v in COMMANDS.items():
        if command in v:
            print(k(**my_arg))
    if command != 'show_all':
        print(show_all())


if __name__ == '__main__':
    main()
