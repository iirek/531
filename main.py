import csv
import typing
import os

from collections import namedtuple, defaultdict
from decimal import Decimal
from io import StringIO
from typing import List, Dict, DefaultDict, NamedTuple


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
    return Decimal(round_to_nearest * round(num / round_to_nearest))


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


if __name__ == "__main__":
    lifts_info = gather_lifts_info()

    lifts_one_rep_max = {
        lift_name: get_one_rep_max(reps_and_weight)
        for (lift_name,reps_and_weight) in
        lifts_info.items()
    }
    lifts_training_one_rep_max = {
        lift_name: get_one_rep_training_max(one_rep_max)
        for (lift_name, one_rep_max) in
        lifts_one_rep_max.items()
    }
    cycle = generate_training_cycle(lifts_training_one_rep_max)
    save_cycle_to_disk(generate_csv_for_cycle(cycle))
