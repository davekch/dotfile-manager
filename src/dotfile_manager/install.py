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


def get_dotfiles(source: Path, only: list[str]=None, exclude: list[str]=None) -> list[Path]:
    """
    return all paths in `source`, skipping all files that have a path in
    `exclude` in their parent
    """
    exclude = [source / e for e in (exclude or [])]
    paths = [source / o for o in (only or ["."])]  # if `only` is empty, use the full source
    # list of all wanted dotfiles to be constructed
    dotfiles = []
    for path in paths:
        if path.is_file() and path not in exclude:
            dotfiles.append(
                path.relative_to(source)
            )
        elif path.is_dir():
            for subdir, _, files in os.walk(path):
                if source / subdir in exclude or any(
                    e in (source / subdir).parents for e in exclude
                ):
                    continue
                for file in files:
                    if (source / subdir / file) in exclude:
                        continue

                    dotfile = Path(subdir).relative_to(source) / file
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
    for dotfile in dotfiles:
        if (homedir / dotfile).exists():
            # check if this file is already linked to the target
            if (homedir / dotfile).is_symlink() and (homedir / dotfile).resolve() == dotpath / dotfile:
                logger.debug(f"file {dotfile} is already linked correctly, skip")
                continue
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
