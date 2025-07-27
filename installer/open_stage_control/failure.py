from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Failure:
    """Failure is a small wrapper for functions and the Exceptions they raise for tracking up the call chain."""

    func: Callable[[], Optional[Exception]]
    error: Exception
