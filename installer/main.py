# Builds, packages, and runs Open Stage Control for Apple Silicon.
# Supports a minimum of Python v3.9.x.


import platform
import sys
from typing import Optional

from open_stage_control import Failure, OpenStageControl

__author__ = "Alex Ruger"


def main():
    # TODO:
    # The version value should not be hard-coded; but at the moment, this is
    # the only version of Open Stage Control that supports Apple Silicon, so
    # for now it's fine.
    # However, in the future this script should automatically retrieve the
    # latest release and use that unless a specific version is explicitly stated.
    osc = OpenStageControl(version="1.29.6")

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
    # The oldest version of macOS that runs on M1 is Big Sur, which I think has
    # Python 2 installed (which we're guarding against) and Python v3.7.3 or
    # v3.8.2 (I've seen both reported; need to confirm which), so let's make
    # sure this script supports down to that.
    major: int = sys.version_info[0]
    minor: int = sys.version_info[1]

    if major < 3:
        raise RuntimeError("This script requires Python 3!")
    if minor < 9:
        raise RuntimeWarning(
            "This script assumes Python 3.9. Cannot guarantee that this will work correctly."
        )

    main()
