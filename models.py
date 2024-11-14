from sqlalchemy import Column, Integer, String, Boolean, LargeBinary
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
