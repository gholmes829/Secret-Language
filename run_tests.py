"""

"""

import os.path as osp, os

from core.utils import run_in_shell


ROOT_PATH = osp.basename(osp.realpath(__file__))
TEST_PATH = osp.join(ROOT_PATH, 'tests')

def main():
    tests = [f'test{i}' for i in range(1, 9)]

    for i, test in enumerate(tests, 1):
        res = run_in_shell(f'python . tests/{test}.lang').strip()
        with open(f'tests/{test}.out', 'r') as f:
            truth = f.read().strip()
        
        if res == truth:
            print(f' - "{test}" passed.')
        else:
            print(f' - "{test}" FAILED!!')


if __name__ == '__main__':
    main()