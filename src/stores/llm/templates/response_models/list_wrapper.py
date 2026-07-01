from __future__ import annotations
from typing import Generic, Iterator, List, Type, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class ListOf(BaseModel, Generic[T]):
    """Generic list wrapper that forces the LLM to return a JSON array
    of any given Pydantic model without requiring a per-model wrapper.

    Usage:
        response_model=ListOf[MCQ]
        response_model=ListOf[MainIdea]
        response_model=ListOf.constrained(MCQ, min_length=1, max_length=5)
    """
    root: List[T] = Field(...)

    def __iter__(self) -> Iterator[T]:
        return iter(self.root)

    @classmethod
    def constrained(cls, item_type: Type, *, min_length: Optional[int] = 1, max_length: Optional[int] = 3) -> type:
        """Return a new ListOf subclass with custom length bounds.

        Args:
            item_type: The Pydantic model class for each list element.
            min_length: Minimum number of items (default 1).
            max_length: Maximum number of items (default 3).
        """
        class ListOf(BaseModel, Generic[T]):
            root: List[item_type] = Field(..., min_length=min_length, max_length=max_length)

            def __iter__(self) -> Iterator[item_type]:
                return iter(self.root)

        return ListOf
