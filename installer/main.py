# Builds, packages, and runs Open Stage Control for Apple Silicon.
# Supports a minimum of Python v3.8.2 on macOS Big Sur.


import platform
import sys
import venv
from pathlib import Path
from typing import Optional

import requests  # NOTE: Requires venv
import semver  # NOTE: Requires venv
from open_stage_control import Failure, OpenStageControl

__author__ = "Alex Ruger"


def in_venv(venv_path: Optional[Path] = None) -> bool:
    """
    Determines if the current process is running in a virtual environment.
    If venv_path is not None, will check if running in a specific virtual environment;
    otherwise will check if running in any virtual environment.
    """
    # TODO: Adapt this code to the new point of this function (see docstring).
    #
    # if sys.prefix != sys.base_prefix and sys.prefix != sys.base_exec_prefix:
    #     if venv_path is not None:
    #
    # return False


def get_interpreter() -> Path:
    """Returns a Path to the current base Python interpreter binary."""
    interpreter: Path = Path(sys.base_prefix).resolve(strict=True)
    if interpreter.is_dir():
        try:
            resolved = interpreter.joinpath("bin", "python3").resolve(strict=True)
        except FileNotFoundError as error:
            raise error
        else:
            return resolved
    return interpreter


def main():
    # TODO:
    # The version value should not be hard-coded.
    # This is the most recent version.
    # The first version to support Apple Silicon is v1.29.6.
    # In the future, this script should automatically retrieve the
    # latest release and use that *unless a specific version is explicitly stated*.
    osc = OpenStageControl(version="1.29.7")

    failures: Optional[list[Failure]] = osc.pre_install()
    if failures is not None:
        for f in failures:
            print(f"Function {f.func} raised the following Exception: {f.error}")
        raise Exception("Failed Open Stage Control pre-install. See above.")

    e: Optional[Exception]
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

    # TODO:
    # The oldest version of macOS that runs on M1 is Big Sur, which has both
    # Python 2 installed (which we're guarding against) and Python v3.8.2.
    major: int = sys.version_info[0]
    minor: int = sys.version_info[1]
    micro: int = sys.version_info[2]

    if major < 3:
        raise RuntimeError("This script requires Python 3!")
    if minor < 8:
        raise RuntimeWarning(
            "This script assumes Python 3.8.2 or higher. Cannot guarantee that this will work correctly."
        )
    if micro < 2:
        raise RuntimeWarning(
            "This script assumes Python 3.8.2 or higher. Cannot guarantee that this will work correctly."
        )

    # TODO: Check for venv at ~/.local/share/osc-as/ and run main() within that via a new process.

    main()
