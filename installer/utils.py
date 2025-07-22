import subprocess
from typing import Optional

from .app import App
from .apps import apps


# Looks like avoiding the xcode installation window is unavoidable, so not using this at the moment.
def install_xcode_cli_tools() -> Optional[Exception]:
    try:
        # FIXME: `shell=True` is famously insecure. Try and figure out another way to do this.
        result: str = (
            subprocess.check_output(["xcode-select -p"], shell=True)
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError:
        try:
            _: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["xcode-select", "--install"]
            )
        except subprocess.CalledProcessError as error:
            return error
    else:
        if result != "/Library/Developer/CommandLineTools":
            try:
                _: subprocess.CompletedProcess[bytes] = subprocess.run(
                    ["xcode-select", "--install"]
                )
            except subprocess.CalledProcessError as error:
                return error
    return None


# FIXME: Homebrew installation is raising `FileNotFoundError: [Errno 2] No such file or directory: 'NONINTERACTIVE=1'`
# TODO: Return values. Exceptions?
def install_dependencies() -> None:
    have_errors: list[App] = []
    for app in apps:
        if app.has_errors() and app not in have_errors:
            have_errors.append(app)
            continue
        error: Optional[Exception] = app.install()
        if error is not None:
            app.errors.append(error)
            if app not in have_errors:
                have_errors.append(app)

    if len(have_errors) > 0:
        print("The following apps encountered errors:")
        for app in have_errors:
            app.print_errors()

    installed: list[App] = [app for app in apps if app.installed]
    if len(installed) == 0:
        print("No apps were installed!")
    else:
        print("The following apps were installed:")
        for app in installed:
            print(app.name)
