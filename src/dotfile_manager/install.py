import os
import sys
from pathlib import Path
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
        logger.debug(f"create directory {destdir}")
        os.makedirs(destdir)

    os.symlink(sourcedir / file, linkdir / file)


def get_dotfiles(path: Path, exclude: list[str]=None) -> list[Path]:
    """
    return all dotfile paths in `path`, skipping all files that have a path in
    `exclude` in their parent
    """
    if exclude:
        exclude = [Path(e) for e in exclude]
    else:
        exclude = []
    dotfiles = []
    for subdir, _, files in os.walk(path):
        if Path(subdir) in exclude or any(
            Path(e) in Path(subdir).relative_to(path).parents for e in exclude
        ):
            continue
        for file in files:
            if file in exclude:
                continue

            dotfile = Path(subdir).relative_to(path) / file
            dotfiles.append(dotfile)

    return dotfiles


def yesno(question):
    answer = input(f"{question} [y/n]: ")
    return answer in ["y", "yes"]


def main_symlinks(
    dotfiles: list[Path],
    dotpath: Path,
    homedir: Path,
    always_overwrite: bool,
    never_overwrite: bool,
    dry: bool,
):
    """
    - dotfiles: list of files to create symlinks for
    - dotpath: source directory
    - homedir: directory to link dotfiles to
    - always_overwrite: overwrite existing files. if false and never_overwrite is false, an interactive prompt appears
    - never_overwrite: don't existing files. if false and always_overwrite is false, an interactive prompt appears
    - dry: run dry
    """
    dotpath = dotpath.resolve()
    homedir = homedir.expanduser().resolve()
    logger.debug(f"{dotfiles=}")
    for dotfile in dotfiles:
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

    # install file-dotfile
    file_dotfile = Path("~/.local/bin/file-dotfile").expanduser()
    if not file_dotfile.exists():
        logger.info("install file-dotfile to ~/.local/bin/")
        if not args.dry:
            os.symlink(Path("file-dotfile.py").resolve(), file_dotfile)

    dotfiles = get_dotfiles(Path(source))
    main_symlinks(
        dotfiles,
        Path(source).expanduser(),
        Path(target).expanduser(),
        args.yes,
        args.no,
        args.dry,
    )
