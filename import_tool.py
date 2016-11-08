import json

from decimal import Decimal
from typing import List, Dict, Union

from main import generate_training_cycle, save_cycle_to_db


def load_data(import_file: str) -> List[Dict[str, Union[int, float]]]:
    with open(import_file, 'r') as f:
        data = json.load(f)

    return data


# convert floats to Decimals
def convert_to_expected_format(data: List[Dict[str, Union[int, float]]])-> List[Dict[str, Decimal]]:
    for cycle in data:
        if 'index' in cycle:
            del cycle['index']
        for lift in cycle:
            cycle[lift] = Decimal(cycle[lift])
    return data


if __name__ == '__main__':
    import sys
    dump_path = sys.argv[1]
    data = load_data(dump_path)
    converted_data = convert_to_expected_format(data)
    for cycle in converted_data:
        generated_cycle = generate_training_cycle(cycle)
        save_cycle_to_db(generated_cycle)
