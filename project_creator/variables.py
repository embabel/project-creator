from dataclasses import dataclass
from typing import List


@dataclass
class Variable:
    """Data class representing a single template variable replacement."""

    old: str
    new: str
    in_path: bool = False


@dataclass
class Variables:
    """Data class to hold a collection of template variable replacements."""

    variables: List[Variable]
