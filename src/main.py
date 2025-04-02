from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Analytics Portal API")

# Включаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class Post(BaseModel):
    id: int
    title: str
    description: str
    link: str
    image_url: Optional[str] = None
    category: str
    created_at: datetime

class Category(BaseModel):
    id: int
    name: str
    description: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    favorite_posts: List[int]

class FavoritePostRequest(BaseModel):
    post_id: int
    user_id: int

# Имитация базы данных
favorite_posts = {}

# Заглушки для API endpoints
@app.get("/api/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: int):
    # Заглушка для профиля пользователя
    return {
        "id": user_id,
        "username": "test_user",
        "email": "test@example.com",
        "favorite_posts": favorite_posts.get(user_id, [])
    }

@app.get("/api/posts", response_model=List[Post])
async def get_posts():
    # Заглушка для списка постов
    return [
        {
            "id": 1,
            "title": "Sample Analytics Post",
            "description": "This is a sample post about analytics",
            "link": "https://example.com/post1",
            "image_url": "https://example.com/image1.jpg",
            "category": "business-analytics",
            "created_at": datetime.now()
        }
    ]

@app.get("/api/categories", response_model=List[Category])
async def get_categories():
    # Заглушка для списка категорий
    return [
        {
            "id": 1,
            "name": "Business Analytics",
            "description": "Articles about business analytics"
        },
        {
            "id": 2,
            "name": "System Analytics",
            "description": "Articles about system analytics"
        }
    ]

@app.get("/api/category/{category_id}/posts", response_model=List[Post])
async def get_category_posts(category_id: int):
    # Заглушка для постов определенной категории
    return [
        {
            "id": 1,
            "title": f"Sample Post in Category {category_id}",
            "description": "This is a sample post",
            "link": "https://example.com/post1",
            "image_url": "https://example.com/image1.jpg",
            "category": f"category-{category_id}",
            "created_at": datetime.now()
        }
    ]

# POST методы для работы с избранными постами
@app.post("/api/favorites/add")
async def add_to_favorites(request: FavoritePostRequest):
    if request.user_id not in favorite_posts:
        favorite_posts[request.user_id] = []
    
    if request.post_id not in favorite_posts[request.user_id]:
        favorite_posts[request.user_id].append(request.post_id)
        return {"message": "Post added to favorites"}
    else:
        raise HTTPException(status_code=400, detail="Post already in favorites")

@app.post("/api/favorites/remove")
async def remove_from_favorites(request: FavoritePostRequest):
    if request.user_id in favorite_posts and request.post_id in favorite_posts[request.user_id]:
        favorite_posts[request.user_id].remove(request.post_id)
        return {"message": "Post removed from favorites"}
    else:
        raise HTTPException(status_code=404, detail="Post not found in favorites")

@app.get("/api/favorites/{user_id}")
async def get_favorites(user_id: int):
    return {"favorite_posts": favorite_posts.get(user_id, [])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 