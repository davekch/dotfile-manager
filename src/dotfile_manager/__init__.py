from dataclasses import dataclass, field
from pathlib import Path
import toml
import os
import logging


logger = logging.getLogger(__name__)


class MisconfigurationError(Exception):
    pass


@dataclass
class Config:
    source: Path   # from where to install dotfiles
    target: Path   # where dotfiles should be installed to
    ignore: list[Path] = field(
        default_factory=lambda: [Path(".git"), Path(".gitignore")]
    )

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        if "source" not in data:
            raise MisconfigurationError("missing configuration for source directory")
        return cls(
            source=Path(data["source"]).expanduser().resolve(),
            target=Path(data.get("target", "~")).expanduser().resolve(),
            ignore=[Path(i) for i in data.get("ignore", [])]
        )

    def to_dict(self) -> dict:
        return {
            "source": str(self.source),
            "target": str(self.target),
            "ignore": [str(i) for i in self.ignore]
        }

    @staticmethod
    def get_default_path() -> Path:
        config_dir = Path(
            os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")
        ) / "dotfile-manager"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.toml"

    @classmethod
    def load(cls, path: str | Path=None) -> "Config":
        if not path:
            path = cls.get_default_path()
        with open(path) as f:
            config_data = toml.load(f)
        return cls.from_dict(config_data)

    def write(self, path: str | Path=None):
        if not path:
            path = self.get_default_path()
        with open(path, "w") as f:
            toml.dump(self.to_dict(), f)
        logger.info(f"saved configuration to {str(path)}")


def init_manager(dotfile_repo: str, home: str):
    config = Config(
        source=Path(dotfile_repo).expanduser().resolve(),
        target=Path(home).expanduser().resolve(),
    )
    config.write()


def setup_logging(verbose: bool):
    if verbose:
        level = logging.DEBUG
        format = "%(levelname)s: %(message)s"
    else:
        level = logging.INFO
        format = "%(message)s"
    logging.basicConfig(level=level, format=format)
