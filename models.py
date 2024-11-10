from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'school_users'

    barcode = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)

