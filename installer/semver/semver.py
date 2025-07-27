class SemVer:
    """SemVer provides an abstraction for working with semantic versioning."""

    # TODO: Deal with ending letters -- a for alpha, b for beta, etc.
    def __init__(self, ver: str):
        if ver == "":
            raise Exception("Version cannot be empty!")
        if ver.startswith("v"):
            ver = ver.removeprefix("v")

        _ver: list[str] = ver.strip().split(".")
        if len(_ver) != 3:
            raise Exception(f"Version should only contain 3 parts: {ver}")

        try:
            _major: str = _ver[0]
        except IndexError as error:
            raise error

        try:
            _minor: str = _ver[1]
        except IndexError as error:
            raise error

        try:
            _micro: str = _ver[2]
        except IndexError as error:
            raise error

        try:
            self._major: int = int(_major)
        except ValueError:
            raise ValueError(f"Version should only contain numbers: {_major}")

        try:
            self._minor: int = int(_minor)
        except ValueError:
            raise ValueError(f"Version should only contain numbers: {_minor}")

        try:
            self._micro: int = int(_micro)
        except ValueError:
            raise ValueError(f"Version should only contain numbers: {_micro}")

    @property
    def major(self) -> int:
        return self._major

    @major.setter
    def major(self, value: int) -> None:
        self._major = value

    @property
    def minor(self) -> int:
        return self._minor

    @minor.setter
    def minor(self, value: int) -> None:
        self._minor = value

    @property
    def micro(self) -> int:
        return self._micro

    @micro.setter
    def micro(self, value: int) -> None:
        self._micro = value

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.micro}"
