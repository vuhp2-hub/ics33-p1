from pathlib import Path
from simulation import Simulation


def _read_input_file_path() -> Path:
    """Reads the input file path from the standard input"""
    return Path(input())


def main() -> None:
    """Runs the simulation program in its entirety"""
    input_file_path = _read_input_file_path()

    if not input_file_path.exists():
        print('FILE NOT FOUND')
        return

    my_simulation = Simulation()

    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            words = line.strip().split()
            if len(words) == 0 or words[0] == '#':
                continue
            if words[0] == 'LENGTH':
                my_simulation.set_length(words[1])
            elif words[0] == 'DEVICE':
                my_simulation.add_device(words[1])
            elif words[0] == 'PROPAGATE':
                my_simulation.add_propagation(words[1], words[2], words[3])
            elif words[0] == 'ALERT':
                my_simulation.add_alert(words[1], words[2], words[3])
            elif words[0] == 'CANCEL':
                my_simulation.add_cancellation_time(words[1], words[2], words[3])

    my_simulation.run()
if __name__ == '__main__':
    main()
