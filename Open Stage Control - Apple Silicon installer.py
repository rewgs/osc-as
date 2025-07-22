# Builds, packages, and runs Open Stage Control for Apple Silicon.
# Supports a minimum of Python v3.9.x.

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

__author__ = "Alex Ruger"


class App:
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


class OpenStageControl:
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

    def download(self) -> Optional[Exception]:
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

    def unzip(self) -> Optional[Exception]:
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

    def install_dependencies(self) -> Optional[Exception]:
        """Runs `npm install` within the downloaded source code directory."""
        os.chdir(self._unzipped_dir)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(["npm", "install"])
        except subprocess.CalledProcessError as error:
            return error
        return None

    def build(self) -> Optional[Exception]:
        """Runs `npm run build` within the downloaded source code directory."""
        os.chdir(self._unzipped_dir)
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["npm", "run", "build"]
            )
        except subprocess.CalledProcessError as error:
            return error
        return None

    def package(self) -> Optional[Exception]:
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


# apps: list[App] = [
#     App(
#         # NOTE: User's shell needs to be updated.
#         name="brew",
#         install_cmd=[
#             "NONINTERACTIVE=1",
#             "/bin/bash -c",
#             "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
#         ],
#     ),
#     # Currently download the OSC source code via curl, so git is unnecessary.
#     # App(name="git", install_cmd=["brew", "install", "git"]),
#     App(name="node", install_cmd=["brew", "install", "node@20"]),
# ]


# Looks like avoiding the xcode installation window is unavoidable, so commenting this out.
#
# def install_xcode_cli_tools() -> Optional[Exception]:
#     try:
#         # FIXME: `shell=True` is famously insecure. Try and figure out another way to do this.
#         result: str = (
#             subprocess.check_output(["xcode-select -p"], shell=True)
#             .decode("utf-8")
#             .strip()
#         )
#     except subprocess.CalledProcessError:
#         try:
#             _: subprocess.CompletedProcess[bytes] = subprocess.run(
#                 ["xcode-select", "--install"]
#             )
#         except subprocess.CalledProcessError as error:
#             return error
#     else:
#         if result != "/Library/Developer/CommandLineTools":
#             try:
#                 _: subprocess.CompletedProcess[bytes] = subprocess.run(
#                     ["xcode-select", "--install"]
#                 )
#             except subprocess.CalledProcessError as error:
#                 return error
#     return None


# FIXME: Homebrew installation is raising `FileNotFoundError: [Errno 2] No such file or directory: 'NONINTERACTIVE=1'`
# TODO: Return values. Exceptions?
# def install_dependencies() -> None:
#     have_errors: list[App] = []
#     for app in apps:
#         if app.has_errors() and app not in have_errors:
#             have_errors.append(app)
#             continue
#         error: Optional[Exception] = app.install()
#         if error is not None:
#             app.errors.append(error)
#             if app not in have_errors:
#                 have_errors.append(app)
#
#     if len(have_errors) > 0:
#         print("The following apps encountered errors:")
#         for app in have_errors:
#             app.print_errors()
#
#     installed: list[App] = [app for app in apps if app.installed]
#     if len(installed) == 0:
#         print("No apps were installed!")
#     else:
#         print("The following apps were installed:")
#         for app in installed:
#             print(app.name)


def main():
    e: Optional[Exception]
    # e = install_xcode_cli_tools()
    # if e is not None:
    #     raise e

    # install_dependencies()

    # TODO:
    # The version value should not be hard-coded; but at the moment, this is
    # the only version of Open Stage Control that supports Apple Silicon, so
    # for now it's fine.
    # However, in the future this script should automatically retrieve the
    # latest release and use that unless a specific version is explicitly stated.
    osc = OpenStageControl(version="1.29.6")

    e = osc.download()
    if e is not None:
        raise e

    e = osc.unzip()
    if e is not None:
        raise e

    e = osc.install_dependencies()
    if e is not None:
        raise e

    e = osc.build()
    if e is not None:
        raise e

    e = osc.package()
    if e is not None:
        raise e

    e = osc.install()
    if e is not None:
        raise e

    e = osc.post_install()
    if e is not None:
        raise e

    print(f"Installed Open Stage Control {osc.version} to {osc.app_dir}")


if __name__ == "__main__":
    if platform.system() != "Darwin":
        raise NotImplementedError(
            f"This script is not supported on {platform.system()}"
        )

    if platform.machine() != "arm64":
        raise NotImplementedError(
            f"This script is not supported on {platform.machine()}"
        )

    major: int = sys.version_info[0]
    minor: int = sys.version_info[1]

    if major < 3:
        raise RuntimeError("This script requires Python 3!")
    if minor < 9:
        raise RuntimeWarning(
            "This script assumes Python 3.9. Cannot guarantee that this will work correctly."
        )

    main()
