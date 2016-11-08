import csv
import typing
import os

from collections import defaultdict
from decimal import Decimal
from io import StringIO
from typing import List, Dict, DefaultDict, NamedTuple, Optional, Union, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Load
from sqlalchemy.sql.functions import coalesce

from models import get_db, Cycle, CycleLiftMax, CycleLiftWeekly, CycleLiftIncrement, LiftIncrement


TWO_PLACES = Decimal(10) ** -2
WEEKS = ['week_1', 'week_2', 'week_3', 'week_4']

lifts = [
    'Press',
    'Deadlift',
    'Bench press',
    'Squat'
]

LiftWeightRep = typing.NamedTuple('LiftWeightRep', [('weight', float), ('reps', str)])
LiftData = typing.NamedTuple('LiftData', [('percentile', int), ('reps', str), ('weight', float)])
IntensityAndReps = NamedTuple('IntensityAndReps', [('percentile', int), ('reps', str)])


def get_weekly_reps_and_intensity() -> Dict[str, List[IntensityAndReps]]:

    weekly_reps = {
        'week_1': [
            IntensityAndReps(percentile=65, reps='5'),
            IntensityAndReps(percentile=75, reps='5'),
            IntensityAndReps(percentile=85, reps='5+'),
        ],

        'week_2': [
            IntensityAndReps(percentile=70, reps='3'),
            IntensityAndReps(percentile=80, reps='3'),
            IntensityAndReps(percentile=90, reps='3+'),
        ],

        'week_3': [
            IntensityAndReps(percentile=75, reps='5'),
            IntensityAndReps(percentile=85, reps='3'),
            IntensityAndReps(percentile=95, reps='1+'),
        ],

        'week_4': [
            IntensityAndReps(percentile=40, reps='5'),
            IntensityAndReps(percentile=50, reps='5'),
            IntensityAndReps(percentile=60, reps='5+'),
        ]
    }

    return weekly_reps


def rounder(num: Decimal) -> Decimal:
    round_to_nearest = Decimal(2.5)
    result = Decimal(round_to_nearest * round(num / round_to_nearest))
    return result


def generate_training_cycle(
    lift_weights: Dict[str, Decimal]
) -> DefaultDict[str, DefaultDict[str, List[LiftData]]]:
    weekly_reps_and_intensity = get_weekly_reps_and_intensity()
    """
    'week_1': {
        'Press': [
            LiftData(percentile=65, reps=5, weight=47.5),
            LiftData(percentile=75, reps=5, weight=52.5),
            LiftData(percentile=85, reps=5+, weight=60)
        ]
        'Deadlift': []
        ...
    }
    """
    calculated_lifts = defaultdict(defaultdict)
    for week in weekly_reps_and_intensity:
        for lift in lift_weights:
            sets = []
            for exercise_set in weekly_reps_and_intensity[week]:
                calculated_set = LiftData(
                    percentile=exercise_set.percentile,
                    reps=exercise_set.reps,
                    weight=rounder(Decimal(
                        ((exercise_set.percentile * lift_weights[lift]) / 100)
                        ).quantize(TWO_PLACES))
                )
                sets.append(calculated_set)
            calculated_lifts[week][lift] = sets

    calculated_lifts['test_max'] = lift_weights
    return calculated_lifts


def generate_csv_for_cycle(cycle: DefaultDict[str, DefaultDict[str, List[LiftData]]]) -> List[StringIO]:
    csv_files = []
    for week in WEEKS:
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow(['Exercise', 'Percentile', 'Weight', 'Reps'])
        for exercise in lifts:
            for exercise_set in cycle[week][exercise]:
                writer.writerow([
                    exercise,
                    exercise_set.percentile,
                    exercise_set.weight,
                    exercise_set.reps
                ])
        csv_files.append(f)
    return csv_files


def gather_lifts_info() -> Dict[str, LiftWeightRep]:
    lifts_info = {}
    for lift in lifts:
        lifts_info[lift] = LiftWeightRep(
            weight=int(input("What weight [{}]?: ".format(lift))),
            reps=int(input("How many reps?: "))
        )

    return lifts_info


def get_one_rep_max(lift: LiftWeightRep) -> Decimal:
    return Decimal(
        Decimal(lift.weight * lift.reps * 0.033)
        +
        lift.weight
    ).quantize(TWO_PLACES)


def get_one_rep_training_max(weight: Decimal) -> Decimal:
    return Decimal(
        weight * Decimal(0.9)
    ).quantize(TWO_PLACES)

def save_cycle_to_disk(csv_files: List[StringIO]):
    base_dir_name = 'cycle'
    all_files = os.listdir()
    cycle_dirs = [dir_name for dir_name in all_files if os.path.isdir(dir_name) and dir_name.startswith(base_dir_name)]
    max_cycle_num = max([int(dir.split('_')[1]) for dir in cycle_dirs], default=0)
    next_cycle_num = max_cycle_num+1
    new_cycle_dirname = "cycle_{}".format(next_cycle_num)
    new_cycle_path = os.path.join(os.curdir, new_cycle_dirname)

    os.makedirs(new_cycle_path)
    for file_name, file_content in zip(WEEKS, csv_files):
        with open(os.path.join(new_cycle_path, '{}.csv'.format(file_name)), 'w') as f:
            f.write(file_content.getvalue())

def save_cycle_to_db(generated_cycle: DefaultDict[str, DefaultDict[str, List[LiftData]]]):
    db = get_db()
    cycle = Cycle()
    for lift in generated_cycle['test_max']:
        cycle_lift = CycleLiftMax(lift=lift, amount=generated_cycle['test_max'][lift], cycle=cycle)
        db.add(cycle_lift)
    for week in range(1,5):
        try:
            week_title = 'week_{}'.format(week)
            for lift in generated_cycle[week_title]:
                for lift_data in generated_cycle[week_title][lift]:
                    cycle_lift_weekly=CycleLiftWeekly(
                        week=week,
                        lift=lift,
                        amount=lift_data.weight,
                        reps=lift_data.reps,
                        percentage=lift_data.percentile,
                        cycle=cycle
                    )
                    db.add(cycle_lift_weekly)


        except KeyError:
            if week != 4:
                print("something's wrong looks like data for week {} is missing".format(week))
            pass 
    db.add(cycle)
    db.commit()
    db.close()

def previous_data_exists() -> bool:
    db = get_db()
    return True if db.query(Cycle).first() else False


def get_latest_cycle() -> Cycle:
    db = get_db()
    return db.query(Cycle).order_by(Cycle.index.desc()).first()


def calculate_new_training_max(
    cycle: Cycle,
    cycle_lift_increments: Optional[Dict[str, Union[Decimal, str]]] = None
) -> Tuple[Dict[str, Decimal], Dict[str, Decimal]]:
    db = get_db()
    incremented_values = {}

    if cycle_lift_increments:
        training_maxes={}
        # get current lift_maxes and figure out what to do next
        current_training_maxes = db.query(
            CycleLiftMax
        ).filter(
            CycleLiftMax.cycle==cycle
        ).all()

        for current_max in current_training_maxes:
            lift = current_max.lift
            if lift in cycle_lift_increments:
                need_to_roll_back = type(cycle_lift_increments[lift]) is str
                if need_to_roll_back:
                    training_maxes[lift] = get_one_rep_training_max(current_max.amount)
                    incremented_values[lift] = training_maxes[lift] - current_max.amount
                else:
                    training_maxes[lift] = Decimal(current_max.amount) + cycle_lift_increments[lift]
                    incremented_values[lift] = cycle_lift_increments[lift]
            else:
                standard_increment = Decimal(db.query(LiftIncrement).filter(LiftIncrement.lift==lift).one().amount)
                training_maxes[lift] = Decimal(current_max.amount) + standard_increment
                incremented_values[lift] = standard_increment



    else:
        new_training_max = db.query(
            CycleLiftMax.lift,
            CycleLiftMax.amount + coalesce(CycleLiftIncrement.amount, LiftIncrement.amount),
          ).outerjoin(
            CycleLiftIncrement, CycleLiftMax.lift==CycleLiftIncrement.lift
        ).join(
            LiftIncrement, CycleLiftMax.lift==LiftIncrement.lift
        ).filter(
            CycleLiftMax.cycle == cycle
        ).all()

        training_maxes = {}

        for row in new_training_max:
            training_maxes[row[0]] = row[1]
        
        for increment in db.query(LiftIncrement).all():
            incremented_values[increment.lift] = increment.amount

    return training_maxes, incremented_values


def save_cycle_increments(increments: Dict[str, Decimal]):
    db = get_db()
    # cant use get_latest_cycle because when you assign object from different session when creating a new one
    # it gets upset, I think
    cycle = db.query(Cycle).order_by(Cycle.index.desc()).first()
    for lift in increments:
        increment = CycleLiftIncrement(lift=lift, amount=increments[lift], cycle=cycle)
        db.add(increment)
    db.commit()


if __name__ == "__main__":
    if previous_data_exists():
        import sys
        most_recent_cycle = get_latest_cycle()
        new_training_max, increments = calculate_new_training_max(
            most_recent_cycle
        )
        new_cycle = generate_training_cycle(new_training_max)
        save_cycle_to_db(new_cycle)
        save_cycle_increments(increments)
        sys.exit()

    else:
        lifts_info = gather_lifts_info()

    lifts_one_rep_max = {
        lift_name: get_one_rep_max(reps_and_weight)
        for (lift_name, reps_and_weight) in
        lifts_info.items()
    }
    lifts_training_one_rep_max = {
        lift_name: get_one_rep_training_max(one_rep_max)
        for (lift_name, one_rep_max) in
        lifts_one_rep_max.items()
    }
    cycle = generate_training_cycle(lifts_training_one_rep_max)
    save_cycle_to_db(cycle)


    save_cycle_to_disk(generate_csv_for_cycle(cycle))
