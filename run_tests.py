"""

"""

import os.path as osp, os

from core.utils import run_in_shell


ROOT_PATH = osp.dirname(osp.realpath(__file__))
TEST_PATH = osp.join(ROOT_PATH, 'tests')

def main():
    files = os.listdir(TEST_PATH)
    tests = filter(lambda f: f.endswith('.lang'), files)

    for i, test in enumerate(tests, 1):
        print(f'{test.upper()}:')
        print((len(test) + 1) * '=')
        res = run_in_shell(f'python . tests/{test}').strip()
        true_file = test.replace('.lang', '.out')
        if true_file in files:
            with open(f'tests/{test}.out', 'r') as f:
                truth = f.read().strip()
            
            if res == truth:
                print(f' - "{test}" passed.')
            else:
                print(f' - "{test}" FAILED!!')
        print(res)
        print('\n\n')


if __name__ == '__main__':
    main()