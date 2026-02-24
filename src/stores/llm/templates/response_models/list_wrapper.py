from __future__ import annotations
from typing import Generic, Iterator, List, TypeVar
from pydantic import RootModel

T = TypeVar("T")

class ListOf(RootModel[List[T]], Generic[T]):
    """Generic list wrapper that forces the LLM to return a JSON array
    of any given Pydantic model without requiring a per-model wrapper.

    Usage:
        response_model=ListOf[MCQ]
        response_model=ListOf[MainIdea]
    """
    root: List[T] = []

    def __iter__(self) -> Iterator[T]:
        return iter(self.root)
