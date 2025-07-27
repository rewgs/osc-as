from .dep import Dep

deps: list[Dep] = [
    Dep(
        # NOTE: User's shell needs to be updated.
        name="brew",
        install_cmd=[
            "NONINTERACTIVE=1",
            "/bin/bash -c",
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
        ],
    ),
    # Currently download the OSC source code via curl, so git is unnecessary.
    # App(name="git", install_cmd=["brew", "install", "git"]),
    Dep(name="node", install_cmd=["brew", "install", "node@20"]),
]
