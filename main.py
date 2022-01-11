"""

"""

import os.path as osp, os
import argparse
import lark
import subprocess
import threading

import ast_gen


LANG_EXT = 'lang'
PARSER_TYPE = 'lalr'
GRAMMAR_F_PATH = osp.join(osp.dirname(osp.realpath(__file__)), 'grammar.lark')

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_f', help='source language input file')
    return parser


def read_file(f_path: str) -> str:
    with open(f_path, 'r') as f:
        return f.read()


def write_to_file(f_path: str, content: str) -> str:
    with open(f_path, 'w') as f:
        f.write(content)
    

def run_in_shell(cmd: str):
    subprocess.run(cmd, shell=True)


def main():
    argparser = make_argparser()
    args = argparser.parse_args()

    program = read_file(args.src_f)
    # print(f'PROGRAM:\n{program}')
    # print()
  
    parser = lark.Lark.open(
        GRAMMAR_F_PATH,
        start = 'root',
        parser = PARSER_TYPE,
        cache = 'grammar.cached',
        transformer = ast_gen.ASTBuilder(),
    )
    ast = parser.parse(program)
    print(ast.unparsed())

    out_dot_path = args.src_f.replace(f'.{LANG_EXT}', '.dot')
    out_png_path = args.src_f.replace(f'.{LANG_EXT}', '.png')

    write_to_file(out_dot_path, ast.to_dot())
    run_in_shell(f'dot -Tpng {out_dot_path} -o {out_png_path}')

    print('Running:')
    ast.interpret()


if __name__ == '__main__':
    main()