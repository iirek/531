import click

from models import Model, Lift, Cycle, LiftIncrement, CycleLiftMax, CycleLiftWeekly

from models import get_engine, get_db


@click.group(chain=True)
def cli():
    pass

@click.command('create')
def create_db():
    Model.metadata.create_all(get_engine(), checkfirst=True)
    print('Created DB')
    db = get_db()
    for lift in ['Press', 'Deadlift', 'Bench press', 'Squat']:
        db.add(Lift(name=lift))
    db.commit()
    print('Added 4 main Lifts...')


@click.command('drop')
def drop_db():
    engine = get_engine()
    Model.metadata.reflect(engine)
    Model.metadata.drop_all(engine)
    print('Dropped DB')



cli.add_command(create_db)
cli.add_command(drop_db)

if __name__ == '__main__':
    cli()

