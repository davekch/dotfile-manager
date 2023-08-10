#!/usr/bin/env python3


import os
import sys
from pathlib import Path
import yaml
from typing import Dict
import logging

logger = logging.getLogger(__name__)


DOTPATH = Path(".")
CONFIG = "dotfile-config.yml"


def create_symlink(sourcedir: Path, linkdir: Path, file: Path) -> Path:
    """
    create a symlink in `linkdir/file` pointing to `sourcedir/file`, creating parent directories if necessary
    """
    destdir = linkdir / file.parent
    if not destdir.exists():
        logger.debug(f"creating directory {destdir}")
        os.makedirs(destdir)

    os.symlink(sourcedir / file, linkdir / file)


def get_dotfiles(path=None, config=None) -> Dict[Path, dict]:
    """
    return all dotfile paths in `path`, annotated by tags in `config`
    """
    config = config or {}
    path = path or config.get("source", DOTPATH)
    exclude = config.get("exclude", [])
    dot_attrs = config.get("dotfiles", {}) or {}

    dotfiles = {}
    for subdir, _, files in os.walk(path):
        if subdir in exclude or any(
            Path(e) in Path(subdir).relative_to(path).parents for e in exclude
        ):
            continue
        for file in files:
            if file in exclude:
                continue

            dotfile = Path(subdir).relative_to(path) / file
            dotfiles[dotfile] = {"tags": set()}
            # iterate over config and set attr if there's a match
            for df, attrs in dot_attrs.items():
                # the entry must either be the full filepath + name or be a
                # directory ending with /
                if str(dotfile) == df or (
                    df.endswith("/") and str(dotfile).startswith(df)
                ):
                    if isinstance(attrs["tags"], list):
                        tags = set(attrs["tags"])
                    else:
                        tags = set([attrs["tags"]])
                    dotfiles[dotfile]["tags"] |= tags

    return dotfiles


def yesno(question):
    answer = input(f"{question} [y/n]: ")
    return answer in ["y", "yes"]


def main_symlinks(
    dotpath: Path,
    homedir: Path,
    config: dict,
    tags: list,
    skip_tags: list,
    always_overwrite: bool,
    never_overwrite: bool,
    dry: bool,
):
    """
    - dotpath: directory to scan for dotfiles
    - homedir: directory to link dotfiles to
    - configfile: path to dotfile-config.yml
    - tags: list of tags to include. if empty, all tags are included
    - skip_tags: list of tags to skip
    - always_overwrite: overwrite existing files. if false and never_overwrite is false, an interactive prompt appears
    - never_overwrite: don't existing files. if false and always_overwrite is false, an interactive prompt appears
    - dry: run dry
    """
    dotfiles = get_dotfiles(dotpath, config)
    dotpath = dotpath.resolve()
    homedir = homedir.resolve()
    logger.debug(f"{dotfiles=}")
    for dotfile, attrs in dotfiles.items():
        # if tags are given, skip files without a required tag
        if tags and not any(t in tags for t in attrs["tags"]):
            logger.debug(f"{dotfile}: has no required tag: skipping")
            continue
        if any(t in skip_tags for t in attrs["tags"]):
            logger.debug(f"{dotfile}: has skip tag: skipping")
            continue

        if (homedir / dotfile).exists():
            if not always_overwrite and not never_overwrite:
                logger.warning(f"{dotfile} already exists")
                if yesno(f"delete {dotfile}?"):
                    logger.debug(f"delete {dotfile}")
                    if not dry:
                        os.remove(homedir / dotfile)
                else:
                    continue
            elif always_overwrite:
                logger.info(f"{dotfile} already exists, delete it")
                if not dry:
                    os.remove(homedir / dotfile)
            elif never_overwrite:
                logger.debug(f"{dotfile} already exists, skip")
                continue

        logger.info(
            f"create symlink {str(homedir / dotfile)} -> {str(dotpath / dotfile)}"
        )
        if not dry:
            create_symlink(dotpath, homedir, dotfile)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="directory of dotfiles")
    parser.add_argument("--target", help="home directory")
    parser.add_argument(
        "-f", "--config-file", default=CONFIG, help="path to config file"
    )
    parser.add_argument(
        "--tags",
        default="",
        help="specify tags to include. if no tags are given, everything is included",
    )
    parser.add_argument("--skip-tags", default="", help="specify tags to skip")
    yesno_group = parser.add_mutually_exclusive_group()
    yesno_group.add_argument(
        "-y", "--yes", action="store_true", help="always replace existing files"
    )
    yesno_group.add_argument(
        "-n", "--no", action="store_true", help="never replace existing files"
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="dry run (does not create or delete any files)",
    )
    parser.add_argument("-v", action="store_true", help="verbose output")
    parser.add_argument("-l", "--list-files", action="store_true", help="list files and tags and exit")

    args = parser.parse_args()
    level = "DEBUG" if args.v else "INFO"
    logging.basicConfig(level=level, format="[%(levelname)-8s] %(message)s")

    if args.dry:
        logger.info("==================== DRY RUN ====================")
        logger.info("no files or symlinks will be created or deleted")
        logger.info("")

    # load config
    with open(args.config_file) as f:
        config = yaml.safe_load(f)

    source = args.source or config.get("source", DOTPATH)
    target = args.target or config.get("target", "~")

    if args.list_files:
        dotfiles = get_dotfiles(Path(source).expanduser(), config)
        for file, attrs in dotfiles.items():
            print(file)
            print(f"    tags: [{', '.join(attrs['tags'])}]")
        sys.exit()

    # install file-dotfile
    file_dotfile = Path("~/.local/bin/file-dotfile").expanduser()
    if not file_dotfile.exists():
        logger.info("installing file-dotfile to ~/.local/bin/")
        if not args.dry:
            os.symlink(Path("file-dotfile.py").resolve(), file_dotfile)

    main_symlinks(
        Path(source).expanduser(),
        Path(target).expanduser(),
        config,
        args.tags.split(",") if args.tags else [],
        args.skip_tags.split(",") if args.skip_tags else [],
        args.yes,
        args.no,
        args.dry,
    )
