import os
import shutil
import ssl
import subprocess
from http.client import HTTPResponse
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from semver import SemVer

from .failure import Failure

# This is the first version to support Apple Silicon.
MINIMUM_VERSION: str = "1.29.6"


# TODO:
def get_latest():
    """
    Returns the newest available version of Open Stage Control via
    https://api.github.com/repos/jean-emmanuel/open-stage-control/releases/latest
    """


def get_versions():
    """Returns a list of all versions compatible with Apple Silicon between MINIMUM_VERSION and LATEST_VERSION."""


class OpenStageControl:
    """OpenStageControl provides an abstraction for working with Open Stage Control."""

    def __init__(self, version: str):
        self.version: str = version
        # TODO: Check if this is a valid URL, make sure it exists, etc.
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

    @staticmethod
    def _test_url(url: str) -> tuple[Optional[HTTPResponse], Optional[Exception]]:
        # ctx: ssl.SSLContext = ssl.SSLContext(protocol=ssl.PROTOCOL_SSLv3)
        try:
            _: tuple[str, ...] = urlparse(url)
        except ValueError as err:
            print(f"Could not parse url: {url}")
            return None, err
        except Exception as err:
            print(f"An unexpected error occurred while checking URL {url}: {err}")
            return None, err
        try:
            with urlopen(url, timeout=5) as response:
                # Check the status code. Status codes in the 200s and 300s generally indicate success
                if response.status >= 200 or response.status < 400:
                    return response, None
                # Does this need an else?
        except URLError as err:
            print(f"Error reaching URL {url}: {err.reason}")
            return None, err
        except TimeoutError as err:
            print(f"Timeout reaching URL {url}")
            return None, err
        except Exception as err:  # Catch any other unexpected errors
            print(f"An unexpected error occurred while checking URL {url}: {err}")
            return None, err

    def _download(self) -> Optional[Exception]:
        """Downloads the source code for self.version to the user's Downloads directory. Returns the Exception if raised, otherwise None."""
        if self._download_dst.exists():
            print(
                f"Open Stage Control v{self.version} already downloaded to {self._download_dst}"
            )
            return None

        response, err = self._test_url(self._url)
        if err is not None:
            raise err
        if response is None:
            raise Exception(f"No response from {self._url}")

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
