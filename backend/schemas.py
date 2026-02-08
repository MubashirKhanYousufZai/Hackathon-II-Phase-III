from pydantic import BaseModel
from typing import Optional, List

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    completed: bool

    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoDelete(BaseModel):
    ids: List[int]

class ChatRequest(BaseModel):
    message: str
