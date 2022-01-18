"""

"""

import sys
import os.path as osp, os
import argparse
import lark
import dill
from icecream import ic

from core.transformer import ASTBuilder
from core import utils


LANG_EXT = 'lang'
PARSER_TYPE = 'earley'  # "lalr" or "earley"
GRAMMAR_F_PATH = osp.join(osp.dirname(osp.realpath(__file__)), 'grammar', 'grammar.lark')


def get_cmd_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('src_f', help='source language input file; use *.pickle to use cached version')
    parser.add_argument('--unparse', '-u', action='store_const', const=True, help='print unparsed code')
    parser.add_argument('--gen_ast', '-g', action='store_const', const=True, help='generate .dot and .png for AST')
    parser.add_argument('--cache', '-c', action='store_const', const=True, help='saves state table and AST')
    return parser.parse_args()

def unparse_ast(ast):
    print(ast.unparsed())

def graph_ast(parse_tree, src_f):
    png_path = src_f.replace('.lang', '.png')
        
    if not osp.isfile(png_path) or osp.getmtime(src_f) > osp.getmtime(png_path):
        lark.tree.pydot__tree_to_png(parse_tree, png_path, rankdir='TB')

    # out_dot_path = src_f.replace(f'.{LANG_EXT}', '.dot')
    # out_png_path = src_f.replace(f'.{LANG_EXT}', '.png')

    # utils.write_to_file(out_dot_path, ast.to_dot())
    # utils.run_in_shell(f'dot -Tpng {out_dot_path} -o {out_png_path}')

def cache_ast(ast, src):
    out_pickle_file = src.replace(f'.{LANG_EXT}', '.pickle')
    with open(out_pickle_file, 'wb') as f:
        dill.dump(ast, f)

def sub_pass(raw_src):
    # probably isn't super necessary
    src = ''
    for line in raw_src.split('\n'):
        try:
            filtered = line[:line.index('#')]
        except:
            filtered = line
        src += filtered.replace(';', '\n')
    return src

def main():
    args = get_cmd_line_args()

    # run cached version
    if args.src_f.endswith('.pickle'):
        with open(args.src_f, 'rb') as f:
            sys.exit(dill.load(f).interpret())

    raw_src = utils.read_file(args.src_f)
    src = sub_pass(raw_src)

    if PARSER_TYPE == 'earley':
        parser = lark.Lark.open(
            GRAMMAR_F_PATH,
            start = 'root',
            parser = PARSER_TYPE,
            propagate_positions = True,
            maybe_placeholders = True,
        )
        transformer = ASTBuilder()
        parse_tree = parser.parse(src)
        prog = transformer.transform(parse_tree)

    else:
        parser = lark.Lark.open(
            GRAMMAR_F_PATH,
            start = 'root',
            parser = PARSER_TYPE,
            cache = osp.join('grammar', 'cached'),
            transformer = ASTBuilder(),
            propagate_positions = True,
            keep_all_tokens = True,
            maybe_placeholders = True,
        )

        prog = parser.parse(src)

    if args.unparse: unparse_ast(prog)
    if args.gen_ast: graph_ast(parse_tree, args.src_f)
    if args.cache: cache_ast(prog, args.src_f)

    sys.exit(prog.interpret())


if __name__ == '__main__':
    main()