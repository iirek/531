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
    print('Added 4 main Lifts')

    for lift in ['Press', 'Deadlift', 'Bench press', 'Squat']:
        increment_amount = 2.5 if 'press' in lift.lower() else 5
        db.add(LiftIncrement(lift=lift, amount=increment_amount))
     
    db.commit()
    print('...and their default increments')


@click.command('drop')
def drop_db():
    engine = get_engine()
    Model.metadata.reflect(engine)
    Model.metadata.drop_all(engine)
    print('Dropped DB')


@click.command('dump_cycles')
def dump_cycles():
    from datetime import datetime
    import json
    db = get_db()
    dump_file_name = 'cycles_dump_{}.json'.format(str(datetime.now().date()))
    data = []
    with open(dump_file_name, 'w') as f:
        for cycle in db.query(Cycle).order_by(Cycle.index):
            cycle_data = {}
            for lift_data in db.query(CycleLiftMax).filter(CycleLiftMax.cycle==cycle):
                # because Decimal is not json serializable by default
                cycle_data[lift_data.lift] = float(lift_data.amount)
            cycle_data['index'] = cycle.index
            data.append(cycle_data)
        json.dump(data, f)



cli.add_command(create_db)
cli.add_command(drop_db)
cli.add_command(dump_cycles)

if __name__ == '__main__':
    cli()

