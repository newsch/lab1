#! /usr/bin/env python3

from typing import List, Optional, Iterator, Dict, Tuple
from itertools import zip_longest

import pycosat
import copy

# problem is list of list of runs
# 0: row runs
# 1: column runs
Problem = List[List[int]]

# solution is 2D grid of yes/no, a list of rows
Solution = List[List[bool]]

# SAT problem in Conjunctive Normal Form
Clause = List[int]
CNF = List[Clause]


def parse_alpha_encoding(src: str) -> Problem:
    """Parse a string of an alpha-encoded nonogram.

    The format is explained more at <https://rosettacode.org/wiki/Nonogram_solver>.
    """
    return [
        [[1 + ord(c) - ord('A') for c in group] for group in l.split()] for l in src.splitlines()
    ]


def print_nonogram(problem: Optional[Problem], solution: Optional[Solution] = None) -> None:
    row_constraints = problem[0]
    col_constraints = problem[1]
    height = len(problem[0])
    width = len(problem[1])

    for i, row_constraint in enumerate(row_constraints):
        if solution is None:
            print('. ' * width, end='')
        else:
            print(' '.join('#' if val else '.' for val in solution[i]), end='')

        if problem is not None:
            print(*row_constraint)
    # print column runs
    if problem is not None:
        for line in zip_longest(*col_constraints):
            print(' '.join(str(val) if val is not None else ' ' for val in line))


def read_file(path: str) -> Iterator[Problem]:
    """Read a file of alpha-encoded nonograms."""
    with open(path) as f:
        txt = f.read()

    for encoded_problem in txt.split('\n\n'):
        yield parse_alpha_encoding(encoded_problem)

def create_possibilities(runs, length):

    def _create_possibilities(runs, mark, min_start, possibility):
        #Base Case: add current possibility and return
        if len(runs) == 0:
            possibilities.append(possibility)
            return
        elif min_start >= len(possibility):
            return
        for start in range(min_start, len(possibility) - runs[0] +1 ):
            #Make a copy of the array for every position that the run can start in
            p_copy = copy.deepcopy(possibility)
            for i in range(start, start+runs[0]):
                if(i < len(possibility)):
                    p_copy[i] = mark
                else:
                   return
            _create_possibilities(runs[1:], mark+1, start + runs[0]+1, p_copy)
    empty_possibility = [0 for i in range(length)]
    possibilities = []
    _create_possibilities(runs, 1, 0, empty_possibility)

    return possibilities

def convert_to_sat(problem: Problem) -> Tuple[CNF, Dict[Tuple[int, int], int]]:
    rows = problem[0]
    cols = problem[1]
    row_possibilities = []
    col_possibilities = []
    #handle row
    for row in rows:
        row_possibilities.append(create_possibilities(row, len(cols)))
    #handle col
    for col in cols:
        col_possibilities.append(create_possibilities(col, len(rows)))

    print("Row: ", row_possibilities)
    print("Col: ", col_possibilities)
    # TODO: return form and mapping to grid locations
    pass


def solve(problem: Problem) -> Optional[Solution]:
    height = len(problem[0])
    width = len(problem[1])

    clauses, names = convert_to_sat(problem)
    res = pycosat.solve(clauses)
    if isinstance(res, str):
        return None

    solution = []
    for y in range(height):
        row = []
        for x in range(width):
            term = names[(x, y)]
            # TODO: get value from response
            pass
            row.append(value)
        solution.append(row)

    return solution


def main():
    import sys
    file = sys.argv[1]
    # TODO: solve nonograms here
    for nonogram in read_file(file):
        # print(nonogram)
        print(nonogram)
        convert_to_sat(nonogram)
        print_nonogram(nonogram)


if __name__ == '__main__':
    main()
