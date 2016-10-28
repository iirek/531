import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey, Sequence
from sqlalchemy.types import Integer, Date, DateTime, Text, Numeric


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
    __tablename__ = 'lifts'

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)


class Cycle(Model):
    __tablename__ = 'cycles'

    id = Column(Integer, primary_key=True)

    start_date = Column(DateTime, default=datetime.datetime.utcnow)

    index = Column(Integer, Sequence('cycle_index_seq'), unique=True)

    cycle_lifts_max = relationship('CycleLiftMax', back_populates='cycle')

    cycle_lifts_weekly = relationship('CycleLiftWeekly', back_populates='cycle')


class LiftIncrement(Model):
    __tablename__ = 'lift_increments'

    id = Column(Integer, primary_key=True)
    
    lift = Column(Text, ForeignKey('lifts.name'))

    increment = Column(Numeric(10,2), nullable=False)


class CycleLiftMax(Model):
    __tablename__ = 'cycle_lift_max'

    id = Column(Integer, primary_key=True)

    lift = Column(Text, ForeignKey('lifts.name'))

    amount = Column(Numeric(10,2), nullable=False)

    cycle_index = Column(Integer, ForeignKey('cycles.index'))

    cycle = relationship('Cycle', back_populates='cycle_lifts_max')



class CycleLiftWeekly(Model):
    __tablename__ = 'cycle_lift_weekly'

    id = Column(Integer, primary_key=True)

    week = Column(Integer, CheckConstraint('week < 5'))

    lift = Column(Text, ForeignKey('lifts.name'))

    amount = Column(Numeric(10,2), nullable=False)

    reps = Column(Text) # needs to be properly fixed to use int and flag to indicate more than x such as 3+ 

    percentage = Column(Integer, nullable=False)

    reps_achieved = Column(Integer)

    cycle_index = Column(Integer, ForeignKey('cycles.index'))

    cycle = relationship('Cycle', back_populates='cycle_lifts_weekly')