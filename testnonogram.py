#! /usr/bin/env python3
import unittest

import nonogram

PROBLEMS = [
    # simple single cell that should be True
    (
        ([[1]],
         [[1]]),
        [[True]]
    ),
    # 2x2 that whould be False
    (
        ([[1], [2]],
         [[1], [1]]),
        None
    ),
    (
        ([[1], [2]],
         [[1], [2]]),
        [[False, True],
         [True,  True]]
    ),
]


class TestNonogram(unittest.TestCase):

    def test_create_possibilities(self):
        EXAMPLES = [
            # runs, length, expected output (as a set of tuples)
            ([1], 1, {(1,)}),
            ([1], 2, {(0, 1),(1, 0)}),
            ([1, 2], 3, set()),  # impossible
            ([1, 2], 4, {(1, 0, 2, 2)}),
            # 3 possibilities
            ([1, 2], 5, {
                (1, 0, 2, 2, 0),
                (1, 0, 0, 2, 2),
                (0, 1, 0, 2, 2),
            }),
            # flipped of above
            ([2, 1], 5, {
                (1, 1, 0, 2, 0),
                (1, 1, 0, 0, 2),
                (0, 1, 1, 0, 2),
            }),
            ([5], 7, {
                (1, 1, 1, 1, 1, 0, 0,),
                (0, 0, 1, 1, 1, 1, 1),
                (0, 1, 1, 1, 1, 1, 0,)
            }),
            ([1, 1, 2], 7, {
                (1, 0, 2, 0, 3, 3, 0,),
                (1, 0, 2, 0, 0, 3, 3),
                (1, 0, 0, 2, 0, 3, 3,),
                (0, 1, 0, 2, 0, 3, 3,)
            }),
        ]
        for i, stuff in enumerate(EXAMPLES):
            runs, length, expected = stuff
            with self.subTest(i=i):
                res = nonogram.create_possibilities(runs, length)
                res = set(tuple(p) for p in res)
                self.assertEqual(expected, res)
    
    def test_solve(self):
        for i, pair in enumerate(PROBLEMS):
            problem, solution = pair
            with self.subTest(problem=i):
                # nonogram.print_nonogram(problem)
                print("Problem",i)
                res = nonogram.solve(problem)
                nonogram.print_nonogram(problem, res)
                self.assertEqual(solution, res)


if __name__ == '__main__':
    unittest.main()