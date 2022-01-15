"""

"""

import sys
import os.path as osp, os
import argparse
import lark
import dill

from core.transformer import ASTBuilder
from core import utils


LANG_EXT = 'lang'
PARSER_TYPE = 'lalr'
GRAMMAR_F_PATH = osp.join(osp.dirname(osp.realpath(__file__)), 'grammar.lark')

def get_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_f', help='source language input file; use *.pickle to use cached version')
    parser.add_argument('--unparse', '-u', action='store_const', const=True, help='print unparsed code')
    parser.add_argument('--gen_ast', '-g', action='store_const', const=True, help='generate .dot and .png for AST')
    parser.add_argument('--cache', '-c', action='store_const', const=True, help='saves state table and AST')
    return parser.parse_args()

def unparse_ast(ast):
    print(ast.unparsed())

def graph_ast(ast, src_f):
    out_dot_path = src_f.replace(f'.{LANG_EXT}', '.dot')
    out_png_path = src_f.replace(f'.{LANG_EXT}', '.png')

    utils.write_to_file(out_dot_path, ast.to_dot())
    utils.run_in_shell(f'dot -Tpng {out_dot_path} -o {out_png_path}')

def cache_ast(ast, src):
    out_pickle_file = src.replace(f'.{LANG_EXT}', '.pickle')
    with open(out_pickle_file, 'wb') as f:
        dill.dump(ast, f)

def main():
    args = get_cmd_line_args()

    # run cached version
    if args.src_f.endswith('.pickle'):
        with open(args.src_f, 'rb') as f:
            sys.exit(dill.load(f).interpret())

    prog = utils.read_file(args.src_f)
  
    parser = lark.Lark.open(
        GRAMMAR_F_PATH,
        start = 'root',
        parser = PARSER_TYPE,
        cache = 'grammar.cached',
        transformer = ASTBuilder(),
    )

    ast = parser.parse(prog)

    if args.unparse: unparse_ast(ast)
    if args.gen_ast: graph_ast(ast, args.src_f)
    if args.cache: cache_ast(ast, args.src_f)

    sys.exit(ast.interpret())


if __name__ == '__main__':
    main()