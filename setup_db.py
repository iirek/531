from models import Model, Lift, Cycle, LiftIncrement, CycleLiftMax, CycleLiftWeekly

from models import get_engine

def create():
    Model.metadata.create_all(get_engine(), checkfirst=True)

def tear_down():
    engine = get_engine()
    Model.metadata.reflect(engine)
    Model.metadata.drop_all(engine)


