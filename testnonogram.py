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