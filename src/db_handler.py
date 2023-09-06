import os

from dotenv import load_dotenv
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    delete,
)
from sqlalchemy.orm import Session, declarative_base, relationship

load_dotenv()

# json serial stuffs
# https://blogs.gnome.org/danni/2013/03/07/generating-json-from-sqlalchemy-objects/

# https://riptutorial.com/sqlalchemy/example/6614/converting-a-query-result-to-dict


# store json stuff
# https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy


# better way to load the session: https://www.youtube.com/watch?v=cH0immwfykI


engine = create_engine(os.getenv("DBCCONNECT_STR"))
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(length=100))
    active = Column(Boolean, default=True)
    filters = relationship(
        "UserFlatFilters", backref="users", passive_deletes=True, passive_updates=True
    )
    flatIDs = relationship(
        "FlatID", backref="users", passive_deletes=True, passive_updates=True
    )
    flatIDs = relationship(
        "Polygons", backref="users", passive_deletes=True, passive_updates=True
    )


class UserFlatFilters(Base):
    __tablename__ = "userflatfilters"
    id = Column(Integer, primary_key=True)
    userID = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    minNumberRooms = Column(Integer)
    maxNumberRooms = Column(Integer)
    minFlatSize = Column(Integer)
    maxFlatSize = Column(Integer)
    maxPrice = Column(Integer)
    wbsVorhanden = Column(Boolean, default=False)


class FlatID(Base):
    __tablename__ = "flatids"
    id = Column(Integer, primary_key=True)
    userID = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    flatID = Column(String(length=100), nullable=False)


class Polygons(Base):
    __tablename__ = "polygons"
    id = Column(Integer, primary_key=True)
    userID = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    polygons = Column(JSON)


# TODO table with cron jobs


def create_base():
    Base.metadata.create_all(engine)


def create_user(email: str, active: bool | None = None) -> int:
    newuser = User(email=email, active=active)
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


def check_user_exists(user_id: int) -> bool:
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return True
        else:
            return False


def get_user_email(user_id: int):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return user.email
        else:
            raise ValueError(f"User with ID {user_id} does not exist")


def get_users() -> list[User]:
    with Session(engine) as session:
        return session.query(User).all()


def update_user(user_id: int, email: str | None = None, active: bool | None = None):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
    if user:
        if email:
            setattr(user, "email", email)
        if active:
            setattr(user, "active", active)
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def delete_user(user_id: int):
    if check_user_exists(user_id):
        with Session(engine) as session:
            # clear old flats for user
            stmt = delete(User).where(User.id == user_id)
            session.execute(stmt)
            session.commit()
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def get_known_flat_ids(user_id: int) -> list[int]:
    if check_user_exists(user_id):
        with Session(engine) as session:
            flats = session.query(FlatID).filter(FlatID.userID == user_id).all()
            return [flat.flatID for flat in flats]
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def replace_known_flat_ids(user_id: int, flat_ids: list[int]):
    if check_user_exists(user_id):
        with Session(engine) as session:
            # clear old flats for user
            stmt = delete(FlatID).where(FlatID.userID == user_id)
            session.execute(stmt)

            for flat_id in flat_ids:
                newflat = FlatID(userID=user_id, flatID=flat_id)
                session.add(newflat)

            session.commit()
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def get_userFlatFilters(user_id: int) -> UserFlatFilters:
    with Session(engine) as session:
        if check_user_exists(user_id):
            return (
                session.query(UserFlatFilters)
                .filter(UserFlatFilters.userID == user_id)
                .first()
            )
        else:
            raise ValueError(f"User with ID {user_id} does not exist")


def set_userFlatFilters(user_id: int, flat_filters: dict):
    if check_user_exists(user_id):
        with Session(engine) as session:
            stmt = delete(UserFlatFilters).where(UserFlatFilters.userID == user_id)
            session.execute(stmt)
            flatFilters = UserFlatFilters(userID=user_id)

            for key, value in flat_filters.items():
                setattr(flatFilters, key, value)
            session.add(flatFilters)
            session.commit()
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def uptdate_userFlatFilters(user_id: int, filters_to_update: dict):
    if check_user_exists(user_id):
        with Session(engine) as session:
            flatFilters = (
                session.query(UserFlatFilters)
                .filter(UserFlatFilters.userID == user_id)
                .first()
            )
            if flatFilters:
                for key, value in filters_to_update.items():
                    setattr(flatFilters, key, value)
                    session.commit()
            else:
                raise ValueError(
                    f"Flatfilters for user with ID {user_id} does not exist"
                )
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def get_polygons(user_id: int) -> dict:
    pass
    if check_user_exists(user_id):
        with Session(engine) as session:
            polygons = (
                session.query(Polygons).filter(Polygons.userID == user_id).first()
            )
            if polygons:
                return polygons.polygons
            else:
                return None
    else:
        raise ValueError(f"User with ID {user_id} does not exist")


def set_polygons(user_id: int, polygons: dict):
    if check_user_exists(user_id):
        with Session(engine) as session:
            # clear old polygons if exists
            stmt = delete(Polygons).where(Polygons.userID == user_id)
            session.execute(stmt)

            new_polygons = Polygons(userID=user_id, polygons=polygons)
            session.add(new_polygons)
            session.commit()
    else:
        raise ValueError(f"User with ID {user_id} does not exist")
