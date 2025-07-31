from dataclasses import dataclass
from pathlib import Path
import toml
import os


class MisconfigurationError(Exception):
    pass


@dataclass
class Config:
    source: Path   # from where to install dotfiles
    target: Path   # where dotfiles should be installed to

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        if "source" not in data:
            raise MisconfigurationError("missing configuration for source directory")
        return cls(
            source=Path(data["source"]).expanduser(),
            target=Path(data.get("target", "~")).expanduser(),
        )

    def to_dict(self) -> dict:
        return {
            "source": str(self.source),
            "target": str(self.target),
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
        with open(path, "wb") as f:
            toml.dump(self.to_dict(), f)
