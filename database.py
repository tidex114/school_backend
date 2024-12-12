from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import dotenv
dotenv.load_dotenv()

DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
MKS_DB_URI = f"mysql+pymysql://{os.getenv('MKS_DB_USER')}:{os.getenv('MKS_DB_PASSWORD')}@{os.getenv('MKS_DB_HOST')}:{os.getenv('MKS_DB_PORT')}/{os.getenv('MKS_DB_NAME')}"


engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

mks_engine = create_engine(MKS_DB_URI)
MksSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mks_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mks_db():
    db = MksSessionLocal()
    try:
        yield db
    finally:
        db.close()