from argparse import ArgumentParser, Namespace
import logging

from dotfile_manager import init_manager


def cli_init(args: Namespace):
    init_manager(args.dotfiles, args.home)


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # command to initialize dotfile manager
    parser_init = subparsers.add_parser("init", help="initialize dotfile manager")
    parser_init.add_argument("dotfiles", metavar="path", help="path to the dotfiles repository")
    parser_init.add_argument("--home", metavar="path", help="target directory for dotfiles (default: $HOME)", default="~")
    parser_init.set_defaults(func=cli_init)

    return parser.parse_args()


def main():
    logging.basicConfig(level="INFO", format="%(message)s")
    args = parse_args()
    args.func(args)
