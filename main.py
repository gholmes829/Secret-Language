"""

"""

import sys
import os.path as osp, os
import argparse
import lark
import subprocess
import dill

import ast_gen


LANG_EXT = 'lang'
PARSER_TYPE = 'lalr'
GRAMMAR_F_PATH = osp.join(osp.dirname(osp.realpath(__file__)), 'grammar.lark')

def make_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_f', help='source language input file')
    parser.add_argument('--unparse', '-u', action='store_const', const=True, help='print unparsed code')
    parser.add_argument('--gen_ast', '-g', action='store_const', const=True, help='generate .dot and .png for AST')
    parser.add_argument('--compile', '-c', action='store_const', const=True, help='saves state table')
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

    if args.src_f.endswith('.pickle'):
        with open(args.src_f, 'rb') as f:
            ast = dill.load(f)
            exit_code = ast.interpret()
            sys.exit(exit_code)

    program = read_file(args.src_f)
  
    parser = lark.Lark.open(
        GRAMMAR_F_PATH,
        start = 'root',
        parser = PARSER_TYPE,
        cache = 'grammar.cached',
        transformer = ast_gen.ASTBuilder(),
    )
    ast = parser.parse(program)

    if args.unparse:
        print(ast.unparsed())

    if args.gen_ast:
        out_dot_path = args.src_f.replace(f'.{LANG_EXT}', '.dot')
        out_png_path = args.src_f.replace(f'.{LANG_EXT}', '.png')

        write_to_file(out_dot_path, ast.to_dot())
        run_in_shell(f'dot -Tpng {out_dot_path} -o {out_png_path}')

    if args.compile:
        out_pickle_file = args.src_f.replace(f'.{LANG_EXT}', '.pickle')
        with open(out_pickle_file, 'wb') as f:
            dill.dump(ast, f)

    exit_code = ast.interpret()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()