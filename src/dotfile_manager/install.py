import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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


def create_symlinks(
    dotfiles: list[Path],
    dotpath: Path,
    homedir: Path,
    always_overwrite: bool=False,
    never_overwrite: bool=True,
    dry: bool=False,
):
    """
    - dotfiles: list of files to create symlinks for
    - dotpath: source directory
    - homedir: directory to link dotfiles to
    - always_overwrite: overwrite existing files. if false and never_overwrite is false, an interactive prompt appears
    - never_overwrite: don't existing files. if false and always_overwrite is false, an interactive prompt appears
    - dry: run dry
    """
    if dry:
        logger.info("==================== DRY RUN ====================")
        logger.info("no files or symlinks will be created or deleted")
        logger.info("")
    dotpath = dotpath.expanduser().resolve()
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
