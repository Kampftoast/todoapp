
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    status: bool = False
    priority: int = 0

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: bool | None = None
    priority: int | None = None