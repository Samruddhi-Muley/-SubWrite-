from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ArticleBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    content: str
    tags: Optional[str] = None  # NEW: Tags field

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None
    tags: Optional[str] = None  # NEW: Tags field

class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ArticleWithAuthor(ArticleResponse):
    author_username: str
    tags_list: List[str] = []  # NEW: Tags as list