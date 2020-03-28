#!/usr/bin/env python3
"""Nonogram solver using SAT.

Usage: `./nonogram.py nonogram_problems.txt`
"""
import copy
import logging
from itertools import zip_longest
import time
from typing import List, Optional, Iterator, Dict, Tuple

import pycosat
from pyeda.inter import *

# problem is list of list of runs
# 0: row runs
# 1: column runs
Problem = List[List[int]]

# solution is 2D grid of yes/no, a list of rows
Solution = List[List[bool]]

# SAT problem in Conjunctive Normal Form
Clause = List[int]
CNF = List[Clause]

logging.basicConfig(level=logging.INFO, format="%(message)s")


def parse_alpha_encoding(src: str) -> Problem:
    """Parse a string of an alpha-encoded nonogram.

    The format is explained more at <https://rosettacode.org/wiki/Nonogram_solver>.
    """
    # remove comments
    src = list(filter(lambda l: l.strip().find(';') != 0 and l.strip() != '', src.splitlines()))

    # problem is only first two lines (anything afterwards is ignored)
    runs = src[0:2]
    return [
        [[1 + ord(c) - ord('A') for c in group] for group in l.split()] for l in runs
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
            print('  ', end='')
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


def create_possibilities(runs: List[int], length: int) -> List[List[int]]:
    """Recursively enumerate the possiblities for a single nonogram row/column given the runs."""
    possibilities = []

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
    _create_possibilities(runs, 1, 0, empty_possibility)

    return possibilities


def convert_to_sat(problem: Problem):
    rows = problem[0]
    cols = problem[1]
    row_possibilities = []
    col_possibilities = []

    # generate cell variables
    height = len(rows)
    width = len(cols)
    variables: Dict[Tuple[int, int], Symbol] = {}
    for y in range(height):
        for x in range(width):
            variables[(x,y)] = exprvar('c_{}_{}'.format(x,y))

    # handle row
    # row/col possibilities are joined with AND, so base case is True
    row_possibilities_CNF = True
    for y, row in enumerate(rows):
        row_possibility = create_possibilities(row, len(cols))
        row_possibilities.append(row_possibility)
        row_possibility_CNF = False
        for cell_possibility in row_possibility:
            cell_CNF = True
            for x, col in enumerate(cell_possibility):
                if col:
                    cell_CNF &= variables[(x, y)]
                else:
                    cell_CNF &= ~variables[(x, y)]
            row_possibility_CNF |= cell_CNF
        row_possibilities_CNF &= row_possibility_CNF

    # handle col
    col_possibilities_CNF = True
    for x, col in enumerate(cols):
        col_possibility = create_possibilities(col, len(rows))
        col_possibilities.append(col_possibility)
        col_possibility_CNF = False
        for cell_possibility in col_possibility:
            cell_CNF = True
            for y, row in enumerate(cell_possibility):
                if row:
                    cell_CNF &= variables[(x, y)]
                else:
                    cell_CNF &= ~(variables[(x, y)])
            col_possibility_CNF |= cell_CNF
        col_possibilities_CNF &= col_possibility_CNF

    logging.debug("Row: %s", row_possibilities_CNF)
    logging.debug("Col: %s", col_possibilities_CNF)

    # combine row and column
    problem = row_possibilities_CNF & col_possibilities_CNF
    return problem, variables


def solve(problem: Problem) -> Optional[Solution]:
    height = len(problem[0])
    width = len(problem[1])

    logging.info('Converting to SAT')
    start = time.process_time()
    sat_problem, names = convert_to_sat(problem)
    stop = time.process_time()
    logging.info("Done: %.3fs", stop - start)
    logging.debug(sat_problem)

    logging.info('Solving problem')
    start = time.process_time()
    terms = sat_problem.tseitin()
    res = terms.satisfy_one()
    stop = time.process_time()
    logging.info("Done: %.3fs", stop - start)

    if res is False:
        # no solution
        return None

    logging.debug(res)

    # names is Dict[Tuple[int, int], Symbol]
    # res is Dict[Symbol, bool]

    # populate with array
    # build array of solutions
    solution = []
    for y in range(height):
        row = []
        for x in range(width):
            term = names[(x, y)]
            if term in res:
                value = res[term]
            else:
                value = False
            row.append(value)
        solution.append(row)

    return solution


def main():
    import sys
    if len(sys.argv) < 2:
        print('Usage: ./nonogram.py NONOGRAM_FILE', file=sys.stderr)
        sys.exit(1)
    file = sys.argv[1]
    for nonogram in read_file(file):
        # print(nonogram)
        solution = solve(nonogram)
        print_nonogram(nonogram, solution)


if __name__ == '__main__':
    main()
