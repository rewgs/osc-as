import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass
class Failure:
    """Failure is a small wrapper for functions and the Exceptions they raise for tracking up the call chain."""

    func: Callable[[], Optional[Exception]]
    error: Exception


class OpenStageControl:
    """OpenStageControl provides an abstraction for working with Open Stage Control."""

    def __init__(self, version: str):
        self.version: str = version
        self._url: str = (
            f"https://github.com/jean-emmanuel/open-stage-control/archive/refs/tags/v{self.version}.zip"
        )
        self._downloads: Path = Path.home().joinpath("Downloads")
        self._download_dst: Path = self._downloads.joinpath(f"v{self.version}.zip")
        self._unzipped_dir: Path = self._downloads.joinpath(
            f"open-stage-control-{self.version}"
        )
        self._dist_dir: Path = self._unzipped_dir.joinpath("dist")
        self._package_dir: Path = self._dist_dir.joinpath(
            "open-stage-control-darwin-arm64"
        )
        self._packaged_app: Path = self._package_dir.joinpath("open-stage-control.app")
        self._app_dir: Path = Path(f"/Applications/Open Stage Control/v{self.version}")
        self._app_dst: Path = self._app_dir.joinpath("Open Stage Control.app")

    @property
    def app_dir(self) -> Path:
        return self._app_dir

    def _download(self) -> Optional[Exception]:
        """Downloads the source code for self.version to the user's Downloads directory. Returns the Exception if raised, otherwise None."""
        if self._download_dst.exists():
            print(
                f"Open Stage Control v{self.version} already downloaded to {self._download_dst}"
            )
            return None

        os.chdir(self._downloads)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                [
                    "curl",
                    "-L",
                    "-O",
                    self._url,
                ]
            )
        except subprocess.CalledProcessError as error:
            return error

        try:
            resolved: Path = self._download_dst.resolve(strict=True)
        except FileNotFoundError as error:
            return error

        if self._download_dst != resolved:
            return FileNotFoundError(self._download_dst)

        return None

    def _unzip(self) -> Optional[Exception]:
        """Unzips the downloaded source code for self.version to the user's Downloads directory. Returns the Exception if raised, otherwise None."""
        if self._unzipped_dir.exists():
            print(
                f"Open Stage Control v{self.version} already unzipped to {self._unzipped_dir}"
            )
            return None

        os.chdir(self._downloads)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["unzip", self._download_dst]
            )
        except subprocess.CalledProcessError as error:
            return error

        try:
            resolved: Path = self._unzipped_dir.resolve(strict=True)
        except FileNotFoundError as error:
            return error

        if self._unzipped_dir != resolved:
            return FileNotFoundError(self._unzipped_dir)

        return None

    def _install_dependencies(self) -> Optional[Exception]:
        """Runs `npm install` within the downloaded source code directory."""
        os.chdir(self._unzipped_dir)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(["npm", "install"])
        except subprocess.CalledProcessError as error:
            return error
        return None

    def _build(self) -> Optional[Exception]:
        """Runs `npm run build` within the downloaded source code directory."""
        os.chdir(self._unzipped_dir)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["npm", "run", "build"]
            )
        except subprocess.CalledProcessError as error:
            return error
        return None

    def _package(self) -> Optional[Exception]:
        """Runs `npm run package` within the downloaded source code directory."""
        os.chdir(self._unzipped_dir)
        env = os.environ.copy()
        env["PLATFORM"] = "darwin"
        env["ARCH"] = "arm64"
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["npm", "run", "package"], env=env
            )
        except subprocess.CalledProcessError as error:
            return error
        return None

    def pre_install(self) -> Optional[list[Failure]]:
        """Downloads Open Stage Control; unzips it; installs required dependencies; builds and packages Open Stage Control."""
        failures: list[Failure] = []

        e: Optional[Exception]

        e = self._download()
        if e is not None:
            failures.append(Failure(func=self._download, error=e))

        e = self._unzip()
        if e is not None:
            failures.append(Failure(func=self._unzip, error=e))

        e = self._install_dependencies()
        if e is not None:
            failures.append(Failure(func=self._install_dependencies, error=e))

        e = self._build()
        if e is not None:
            failures.append(Failure(func=self._build, error=e))

        e = self._package()
        if e is not None:
            failures.append(Failure(func=self._package, error=e))

        if len(failures) != 0:
            return failures

        return None

    def install(self) -> Optional[Exception]:
        """Copies the packaged application to the user's Application folder."""
        os.chdir(self._package_dir)
        if not self._app_dir.exists():
            self._app_dir.mkdir(parents=True, exist_ok=True)
        try:
            _: Path = shutil.copytree(
                self._packaged_app, self._app_dst, dirs_exist_ok=True
            )
        # NOTE: This *silently* deletes the application from the Applications directory!
        except FileExistsError:
            try:
                shutil.rmtree(self._app_dir)
            except OSError as error:
                return error
            try:
                _: Path = shutil.copytree(self._packaged_app, self._app_dir)
            except Exception as error:
                return error
        except Exception as error:
            return error
        return None

    def post_install(self) -> Optional[Exception]:
        """Cleans up after itself -- deletes the .zip and unzipped directory."""
        if self._unzipped_dir.exists():
            try:
                shutil.rmtree(self._unzipped_dir)
            except OSError as error:
                return error
        if self._download_dst.exists():
            try:
                self._download_dst.unlink()
            except FileNotFoundError as error:
                return error
        return None
