from sqlalchemy import DateTime, LargeBinary
from sqlalchemy import Float

from sqlalchemy import TIMESTAMP, Column, Integer, SmallInteger, String, Date, DECIMAL, CHAR
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()

class User(Base):
    __tablename__ = 'school_users'

    barcode = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    remaining_balance = Column(DECIMAL(10, 2), nullable=True)


class DirectoryPhoto(Base):
    __tablename__ = 'directory_photos'
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
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

class PomfretStudent(Base):
    __tablename__ = 'pomfret_student'

    id_number = Column(String(15), primary_key=True, nullable=False)
    barcode = Column(String(20), nullable=False)
    student = Column(String(35), nullable=False)
    last_name = Column(String(35), nullable=False)
    present = Column(DECIMAL(9, 2), nullable=False)
    nickname = Column(String(20), nullable=True)
    graduation = Column(Date, nullable=False)
    accnt_type = Column(CHAR(3), nullable=False)
    uid = Column(String(45), nullable=False)
    counter = Column(Integer, primary_key=True, autoincrement=True)

class PomfretTransfer(Base):
    __tablename__ = 'pomfret_transfer'

    id_number = Column(String(15), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    payment = Column(CHAR(2), nullable=False)
    qdate = Column(Date, nullable=False)
    reference = Column(String(20), nullable=False)
    batch = Column(String(20), nullable=False)
    time = Column(String(8), nullable=False)
    sequence = Column(String(10), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    counter = Column(Integer, primary_key=True, autoincrement=True)
