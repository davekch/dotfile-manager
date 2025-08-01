from pathlib import Path
import os
import logging


logger = logging.getLogger(__name__)


def replace_with_symlink(file: Path, source: Path, target: Path):
    """
    move `file` to `source` (the dotfiles repository), replicating `file`'s relative
    location to `target` (the home directory / common root of all dotfiles) and create
    a symlink to the moved file in `source`
    """
    file = file.expanduser().absolute()
    if file.is_symlink():
        logger.error(f"cannot add {file} to dotfiles repository: is a symlink")
        return
    if target not in file.parents:
        logger.error(f"cannot add file {file} to dotfiles repository: file is not in the configured target directory ({target})")
        return
    if not file.exists():
        logger.error(f"file not found: {file}")
        return
    dotfile_path = source / file.relative_to(target)
    logger.debug("move file to dotfiles repository")
    if not dotfile_path.parent.exists():
        logger.debug("directory does not exist in dotfiles repository, create")
        os.makedirs(dotfile_path.parent)
    os.rename(file, dotfile_path)
    logger.debug("create symlink to moved file")
    os.symlink(dotfile_path, file)
    logger.info(f"replaced {file} with symlink to {dotfile_path}")


def replace_many_with_symlinks(files: list[Path], source: Path, target: Path):
    for file in files:
        replace_with_symlink(file, source, target)
