from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str
    source_url: Optional[str] = None
    category_id: int
    tags: List[int] = []

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    category: Category
    tags: List[Tag]

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    post_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    user: User

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    post_id: int
    user_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    created_at: datetime
    post: Post
    user: User

    class Config:
        from_attributes = True 