
from typing import Any, List
from pydantic import BaseModel


class Page(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
