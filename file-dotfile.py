#!/usr/bin/env python3

from pathlib import Path
import sys
import os
import logging
import yaml

REPODIR = Path(__file__).parent
sys.path.insert(0, REPODIR)

import install

logger = logging.getLogger(__name__)


def get_abs_paths(files: list, config: Path = install.CONFIG) -> list:
    """
    get the source and target absolute paths for `files`
    """
    with open(args.config_file) as f:
        config = yaml.safe_load(f)
    sourcedir = Path(config["source"]).expanduser()
    targetdir = Path(config["target"]).expanduser()
    # if source or target are not absolute, assume relative paths to this repo
    if not sourcedir.is_absolute():
        sourcedir = (REPODIR / sourcedir).resolve()
    if not targetdir.is_absolute():
        targetdir = (REPODIR / targetdir).resolve()

    paths = []
    for file in files:
        source = Path(file).resolve()
        # note that in the config, source and target are named from
        # the POV of installing dotfiles from the repo, hence "sourcedir"
        # refers to the repository and "targetdir" refers to HOME.
        # here, we want to move a file from its original path to the
        # repository, keeping the folder structure relative to HOME.
        target = sourcedir / source.relative_to(targetdir)
        paths.append((source, target))
    return paths


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level="INFO", format="[%(levelname)-8s] %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument(
        "-f",
        "--config-file",
        default=REPODIR / install.CONFIG,
        help="path to config file",
    )
    args = parser.parse_args()

    for original, moved in get_abs_paths(args.files, args.config_file):
        logger.info(f"replacing {original} with symlink to {moved}")
        if not moved.parent.exists():
            os.makedirs(moved.parent)
        os.rename(original, moved)
        os.symlink(moved, original)
