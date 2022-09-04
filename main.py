import argparse
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

from models import ContactPerson


engine = create_engine("sqlite:///ab.db")
Session = sessionmaker(bind=engine)
session = Session()


def add(cname, cphone, cemail=None, caddress=None, *args, **kwargs):
    contact = ContactPerson(
        name=cname,
        email=cemail,
        cell_phone=cphone,
        address=caddress,
        )
    session.add(contact)
    session.commit()
    print('Contact added')


def update_contact(cid, cname, cphone, cemail, caddress):
    session.execute(update(ContactPerson).
                    where(ContactPerson.id == cid).
                    values(name = cname, email = cemail, phone = cphone, address = caddress))

    session.commit()
    print('Contact changed')


def show_all(*args, **kwargs):
    contacts = session.query(ContactPerson).all()
    for c in contacts:
        print(vars(c))


def remove(cid, *args, **kwargs):
    contact = session.query(ContactPerson).filter(ContactPerson.id == cid).delete()
    session.commit()
    print('Contact removed')


COMMANDS = {show_all: 'show_all', add: 'add', update_contact: 'update', remove: 'remove'}


def main():
    parser = argparse.ArgumentParser(description='AddressBook APP')
    parser.add_argument('--command', help='Command: show_all, add, update, remove + id')
    parser.add_argument('--name')
    parser.add_argument('--phone')
    parser.add_argument('--email')
    parser.add_argument('--address')
    parser.add_argument('--id')

    arguments = parser.parse_args()
    print(arguments)
    my_arg = vars(arguments)
    print(my_arg)

    command = my_arg.get('command')
    _id = my_arg.get('id')
    name = my_arg.get('name')
    phone = my_arg.get('phone')
    email = my_arg.get('email')
    address = my_arg.get('address')
    for k, v in COMMANDS.items():
        if command in v:
            k(cname=name, cphone=phone, cemail=email, caddress=address, cid=_id)


if __name__ == '__main__':
    main()
