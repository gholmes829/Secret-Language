"""

"""

import os.path as osp, os
from tqdm.contrib.concurrent import thread_map

from icecream import ic
from core.utils import run_in_shell


ROOT_PATH = osp.dirname(osp.realpath(__file__))
TEST_PATH = osp.join(ROOT_PATH, 'tests')

def main():
    files = os.listdir(TEST_PATH)
    tests = list(filter(lambda f: f.endswith('.lang'), files))

    passed = set()
    failed = set()
    na = set()

    print()
    def run_test(test):
        true_file = test.replace('.lang', '.out')  #  > tests/{test.replace(".lang", ".out")}
        if true_file in files:
            res = run_in_shell(f'python . tests/{test}').strip()
            with open(f'tests/{true_file}', 'r') as f:
                truth = f.read().strip()
            
            if res == truth:
                passed.add(test)
            else:
                failed.add(test)
        else:
            na.add(test)
        
    thread_map(run_test, tests)

    tests_ran = len(tests) - len(na)

    print()
    # if passed:
    #     print('The following test cases PASSED')
    #     print('===============================')
    #     for s in passed:
    #         print(f' - "{s}"')
    # else:
    #     print('<-- Oof, no test cases succeeded :( -->')
    #     print('=======================================')

    # print('\n\n')

    if na:
        print('Did not find "*.out" file for following')
        print('=======================================')
        for n in na:
            print(f' - "{n}"')


    if failed:
        print('\n')
        print('The following test cases FAILED')
        print('===============================')
        for f in failed:
            print(f' - "{f}"')
    #else:
    #    print('<-- Yay, all tests succeeded! -->')
    

    print('\n')
    print('TEST SUMMARY')
    print('============')
    print(f' - {len(passed)}/{tests_ran} ({round(100 * len(passed) / tests_ran, 3)}%) passed')
    #print(f' - {len(na)}/{num_tests} ({round(100 * len(na) / num_tests, 3)}%) NA')


if __name__ == '__main__':
    main()