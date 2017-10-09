from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

DB_CONNECTION_STRING = 'postgresql://postgres:nycgi4oKFEyEpBm6@35.197.210.145:5432/postgres'


engine = create_engine(DB_CONNECTION_STRING)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __repr__(self):
        return f'<User(name={self.name}, fullname={self.fullname}>'
