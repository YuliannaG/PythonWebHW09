from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ContactPerson(Base):
    __tablename__ = 'contact_persons'
    id = Column(Integer(), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column('email', String(100), nullable=False)
    cell_phone = Column('cell_phone', String(100), nullable=True)
    address = Column('address', String(100), nullable=False)

    def __repr__(self) -> str:
        return f'{self.id} -  {self.name} {self.email} {self.cell_phone} {self.address}'
