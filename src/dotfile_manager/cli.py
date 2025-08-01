from argparse import ArgumentParser, Namespace
import logging
from pathlib import Path

from dotfile_manager import init_manager, Config, setup_logging
from dotfile_manager.install import create_symlinks, get_dotfiles


logger = logging.getLogger(__name__)


def cli_init(args: Namespace):
    init_manager(args.dotfiles, args.home)


def cli_install(args: Namespace):
    config = Config.load()
    if args.source:
        source = Path(args.source).expanduser().resolve()
    else:
        source = config.source
    if args.target:
        target = Path(args.target).expanduser().resolve()
    else:
        target = config.target

    dotfiles = get_dotfiles(source)
    create_symlinks(
        dotfiles=dotfiles,
        dotpath=source,
        homedir=target,
        always_overwrite=args.yes,
        never_overwrite=args.no,
        dry=args.dry,
    )


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # command to initialize dotfile manager
    parser_init = subparsers.add_parser("init", help="initialize dotfile manager")
    parser_init.add_argument("dotfiles", metavar="path", help="path to the dotfiles repository")
    parser_init.add_argument("--home", metavar="path", help="target directory for dotfiles (default: $HOME)", default="~")
    parser_init.set_defaults(func=cli_init)

    # command to install dotfiles
    parser_install = subparsers.add_parser("install", help="create symlinks for dotfiles")
    parser_install.add_argument("--source", help="directory of dotfiles")
    parser_install.add_argument("--target", help="home directory")
    yesno_group = parser_install.add_mutually_exclusive_group()
    yesno_group.add_argument(
        "-y", "--yes", action="store_true", help="always replace existing files"
    )
    yesno_group.add_argument(
        "-n", "--no", action="store_true", help="never replace existing files"
    )
    parser_install.add_argument(
        "--dry",
        action="store_true",
        help="dry run (does not create or delete any files)",
    )
    parser_install.set_defaults(func=cli_install)

    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(args.verbose)
    args.func(args)
