from sqlalchemy import DateTime, LargeBinary
from sqlalchemy import Float

from sqlalchemy import Column, Integer, SmallInteger, String, Date, DECIMAL, CHAR
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()

class User(Base):
    __tablename__ = 'school_users'

    barcode = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    remaining_balance = Column(DECIMAL(10, 2), nullable=True)


class DirectoryPhoto(Base):
    __tablename__ = 'directory_photos'

    email = Column(String(100), primary_key=True, unique=True, nullable=False)
    photo = Column(LargeBinary, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    transaction_place = Column(String(100), nullable=False)
    transaction_sum = Column(Float, nullable=False)
    items = Column(String(255), nullable=False)
    transaction_date = Column(DateTime, nullable=False)

class NewTransaction(Base):
    __tablename__ = 'pomfret_transact'

    id_number = Column(String(15), nullable=False)  # Student ID or unique identifier
    location = Column(SmallInteger, nullable=False)  # Location of transaction
    qdate = Column(Date, nullable=False)  # Transaction date
    item = Column(String(50), nullable=False)  # Item purchased
    qty = Column(SmallInteger, nullable=False)  # Quantity of items
    amount = Column(DECIMAL(8, 2), nullable=False)  # Amount for the transaction
    payment = Column(CHAR(2), nullable=False)  # Payment method/flag
    time = Column(String(8), nullable=False)  # Transaction time
    counter = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier for each transaction
