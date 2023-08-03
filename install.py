#!/usr/bin/env python3


import os
from pathlib import Path
import yaml
from collections import defaultdict
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


def get_dotfiles(path=DOTPATH, configfile=CONFIG) -> Dict[Path, dict]:
    """
    return all dotfile paths in `path`, annotated by tags in `configfile`
    """
    with open(configfile) as f:
        config = yaml.safe_load(f)
    exclude = config.get("exclude", {})
    dot_attrs = config.get("dotfiles", {})

    dotfiles = {}
    for subdir, _, files in os.walk(path):
        if subdir in exclude or any(Path(e) in Path(subdir).parents for e in exclude):
            continue
        for file in files:
            if file in exclude:
                continue

            dotfile = Path(subdir) / file
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
    configfile: Path,
    tags: list,
    skip_tags: list,
    overwrite: bool,
    dry: bool,
):
    """
    - dotpath: directory to scan for dotfiles
    - homedir: directory to link dotfiles to
    - configfile: path to dotfile-config.yml
    - tags: list of tags to include. if empty, all tags are included
    - skip_tags: list of tags to skip
    - overwrite: overwrite existing files. if false, an interactive prompt appears
    - dry: run dry
    """
    dotfiles = get_dotfiles(dotpath, configfile)
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
            logger.warning(f"{dotfile} already exists")
            if dry:
                pass
            elif overwrite or yesno("overwrite?"):
                os.remove(homedir / dotfile)
            else:
                continue

        if not dry:
            create_symlink(dotpath, homedir, dotfile)
        logger.info(
            ("will create " if dry else "created ")
            + f"symlink {str(homedir / dotfile)} -> {str(dotpath / dotfile)}"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=DOTPATH)
    parser.add_argument("--target", default="~")
    parser.add_argument("-f", "--config-file", default=CONFIG)
    parser.add_argument("--tags", default="")
    parser.add_argument("--skip-tags", default="")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("-v", action="store_true")

    args = parser.parse_args()
    level = "DEBUG" if args.v else "INFO"
    logging.basicConfig(level=level, format="[%(levelname)-8s] %(message)s")

    main_symlinks(
        Path(args.source).expanduser(),
        Path(args.target).expanduser(),
        Path(args.config_file),
        args.tags.split(",") if args.tags else [],
        args.skip_tags.split(",") if args.skip_tags else [],
        args.yes,
        args.dry,
    )
