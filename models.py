from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Date, DateTime, Text, Boolean, Float, Text, Timestamp


from sqlalchemy.ext.declarative import declarative_base

DB_URI = 'postgresql://postgres@localhost/postgres'
def get_engine():
    engine = create_engine(DB_URI, pool_recycle=3600)
    return engine

def get_db():
    engine = get_engine()

    db_session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    ))

    return db_session

Model = declarative_base(bind=get_engine())


class Lift(Model):
    __tablename = 'lifts'

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)


class Cycle(Model):
    __tablename__ = 'cycles'

    id = Column(Integer, primary_key=True)

    start_date = Column(DateTime)

    index = Column(Integer, unique=True)


class LiftIncrement(Model):
    __tablename__ = 'lift_increments'

    id = Column(Integer, primary_key=True)
    


class CycleLifMax(Model):
    __tablename__ = 'cycle_lift_max'


class CycleLiftWeekly(Model):
    __tablename__ = 'cycle_lift_weekly'