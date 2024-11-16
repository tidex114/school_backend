from sqlalchemy import create_engine, asc, Column, Integer, String, Float, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = 'school_users'

    barcode = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)


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

