import shutil
import subprocess
from pathlib import Path
from typing import Optional


class Dep:
    """Dep provides a wrapper for dependencies required for running Open Stage Control from source."""

    @staticmethod
    def _str_to_path(p: str) -> tuple[Optional[Path], Optional[Exception]]:
        """Takes a string and returns it as a resolved Path. If an Exception is raised, it is returned."""
        try:
            path: Path = Path(p)
        except Exception as error:
            return None, error
        try:
            resolved: Path = path.resolve(strict=True)
        except Exception as error:
            return None, error
        else:
            return resolved, None

    def _get_path(self) -> None:
        """Gets path and updates installed accordingly."""
        p: Optional[str] = shutil.which(self.name)
        if p is not None:
            path, error = self._str_to_path(p)
            if error is not None:
                self.errors.append(error)
            if path is not None:
                self.installed = True
                self.path = path

    def __init__(self, name: str, install_cmd: list[str]):
        self.name: str = name
        self.install_cmd: list[str] = install_cmd
        self.installed: bool = False
        self.path: Optional[Path] = None
        self.errors: list[Exception] = []

        self._get_path()

    def install(self) -> Optional[Exception]:
        if not self.installed:
            try:
                _: subprocess.CompletedProcess[bytes] = subprocess.run(self.install_cmd)
            except subprocess.CalledProcessError as error:
                return error
        return None

    def num_errors(self) -> int:
        return len(self.errors)

    def has_errors(self) -> bool:
        if self.num_errors() > 0:
            return True
        return False

    def print_errors(self) -> None:
        if self.has_errors():
            if self.num_errors() == 1:
                print(f"An error occurred with {self.name}:")
                print(self.errors[0])
            else:
                print(f"The following errors occurred with {self.name}:")
                for error in self.errors:
                    print(error)
