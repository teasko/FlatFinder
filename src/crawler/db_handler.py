import json
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine, delete
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import os
from typing import Any

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(length=100))
    active = Column(Boolean, default=True)

class UserFlatFilters(Base):
    __tablename__ = 'userflatfilters'
    id = Column(Integer, primary_key=True)
    userID = Column(Integer,ForeignKey("users.id"), nullable=False)
    minNumberRooms = Column(Integer)
    maxNumberRooms = Column(Integer)
    minFlatSize = Column(Integer)
    maxFlatSize = Column(Integer)
    maxPrice = Column(Integer)
    wbsVorhanden = Column(Boolean, default=False)

class Flat(Base):
    __tablename__ = 'flats'
    id = Column(Integer, primary_key=True)
    userID = Column(Integer,ForeignKey("users.id"), nullable=False)
    flatID = Column(String(length=100), nullable=False)


def create_base():

    engine = create_engine(os.getenv('DBCCONNECT_STR'))
    Base.metadata.create_all(engine)


def create_user(email:str) -> int:
    newuser = User(email = email)
    engine = create_engine(os.getenv('DBCCONNECT_STR'))
    with Session(engine) as session:
        user = session.query(User).filter(User.email == email).first()
        if user:
            return -1
        else:
            session.add(newuser)
            session.flush()
            session.refresh(newuser)
            created_id = newuser.id
            session.commit()
            return created_id

def check_user_exists(user_id:int)->bool:
    engine = create_engine(os.getenv('DBCCONNECT_STR'))
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return True
        else:
            return False

def get_known_flats(user_id:int)->list[Flat]:

    user_exists = check_user_exists(user_id)
    if user_exists:
        engine = create_engine(os.getenv('DBCCONNECT_STR'))
        with Session(engine) as session:
            flats = session.query(Flat).filter(Flat.userID == user_id).all()
            #return [result.flatID for result in results]
            return flats
    else: 
        raise ValueError(f"User with ID {user_id} does not exist")

def get_known_flat_ids(user_id:int)->list[int]:
    flats = get_known_flats(user_id)
    return [flat.flatID for flat in flats]


def replace_known_flats(user_id:int,flat_ids:list[int]):
    user_exists = check_user_exists(user_id)
    if user_exists:
        engine = create_engine(os.getenv('DBCCONNECT_STR'))
        with Session(engine) as session:
            ## clear old flats for user
            stmt = delete(Flat).where(Flat.userID == user_id )
            session.execute(stmt)

            for flat_id in flat_ids:
                newflat = Flat(userID = user_id, flatID=flat_id)
                session.add(newflat)
                
            session.commit()
    else: 
        raise ValueError(f"User with ID {user_id} does not exist")




def get_userFlatFilters(user_id:int) -> list[UserFlatFilters]:
    engine = create_engine(os.getenv('DBCCONNECT_STR'))
    with Session(engine) as session:

        user_exists = check_user_exists(user_id)
        if user_exists:
            return session.query(UserFlatFilters).filter(UserFlatFilters.userID == user_id).first()
        else: 
            raise ValueError(f"User with ID {user_id} does not exist")

def set_userFlatFilters(user_id:int, flat_filters:dict):
    user_exists = check_user_exists(user_id)
    if user_exists:
        engine = create_engine(os.getenv('DBCCONNECT_STR'))
        with Session(engine) as session:
            stmt = delete(UserFlatFilters).where(UserFlatFilters.userID == user_id )
            session.execute(stmt)
            flatFilters = UserFlatFilters(userID=user_id)
            
            for key, value in flat_filters.items():
                setattr(flatFilters, key, value)       
            session.add(flatFilters)
            session.commit()
    else: 
        raise ValueError(f"User with ID {user_id} does not exist")
    

def uptdate_userFlatFilters(user_id:int, filters_to_update:dict):
    engine = create_engine(os.getenv('DBCCONNECT_STR'))
    with Session(engine) as session:
        flatFilters = session.query(UserFlatFilters).filter(UserFlatFilters.userID == user_id).first()
        if flatFilters:
            for key, value in filters_to_update.items():
                setattr(flatFilters, key, value)
                session.commit()
        else:
            raise ValueError(f"Flatfilters for user with ID {user_id} does not exist")

def rows2dict(rows):
    res = []
    for row in rows:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))

    res.append(d)
    return res

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d