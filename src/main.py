from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from typing import List, Optional
from datetime import datetime
from . import models, schemas
from .database import SessionLocal, engine
from passlib.context import CryptContext

# Создаем таблицы при запуске
try:
    # Создаем ENUM тип, если он не существует
    with engine.connect() as conn:
        # Проверяем существование типа
        result = conn.execute(text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole')"
        )).scalar()
        if not result:
            conn.execute(text(
                "CREATE TYPE userrole AS ENUM ('ADMIN', 'MODERATOR', 'USER')"
            ))
            conn.commit()

    # Создаем таблицы с проверкой существования
    models.Base.metadata.create_all(bind=engine, checkfirst=True)
except Exception as e:
    print(f"Error during database initialization: {e}")
    # Продолжаем выполнение, так как таблицы могут уже существовать

app = FastAPI(
    title="MAI Backend API",
    description="API для блог-платформы",
    version="1.0.0",
    root_path="/api"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создание пользователя
@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Проверяем, существует ли пользователь с таким email
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Хешируем пароль
        hashed_password = pwd_context.hash(user.password)
        
        # Создаем пользователя
        db_user = models.User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Поиск постов
@app.get("/search", response_model=List[schemas.Post])
async def search_posts(q: str = Query(..., description="Search query"), db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(
        or_(
            models.Post.title.ilike(f"%{q}%"),
            models.Post.content.ilike(f"%{q}%")
        )
    ).all()
    return posts

# Получение всех постов
@app.get("/posts", response_model=List[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

# Получение конкретного поста
@app.get("/posts/{post_id}", response_model=schemas.Post)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Создание нового поста
@app.post("/posts", response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # Проверяем существование категории
    category = db.query(models.Category).filter(models.Category.id == post.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Создаем пост
    db_post = models.Post(
        title=post.title,
        content=post.content,
        source_url=post.source_url,
        category_id=post.category_id,
        created_at=datetime.utcnow()
    )
    
    # Добавляем теги
    if post.tags:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(post.tags)).all()
        db_post.tags = tags
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Обновление поста
@app.patch("/posts/{post_id}", response_model=schemas.Post)
async def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Обновляем только предоставленные поля
    post_data = post.dict(exclude_unset=True)
    
    # Если указана новая категория, проверяем её существование
    if 'category_id' in post_data:
        category = db.query(models.Category).filter(models.Category.id == post_data['category_id']).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Обновляем поля
    for field, value in post_data.items():
        if field != 'tags':
            setattr(db_post, field, value)
    
    # Обновляем теги, если они предоставлены
    if 'tags' in post_data and post_data['tags'] is not None:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(post_data['tags'])).all()
        db_post.tags = tags
    
    db.commit()
    db.refresh(db_post)
    return db_post

# Удаление поста
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

# Получение всех категорий
@app.get("/categories", response_model=List[schemas.Category])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

# Создание новой категории
@app.post("/categories", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id,
        created_at=datetime.utcnow()
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Получение всех тегов
@app.get("/tags", response_model=List[schemas.Tag])
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(models.Tag).all()
    return tags

# Создание нового тега
@app.post("/tags", response_model=schemas.Tag)
async def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# Получение всех комментариев
@app.get("/comments", response_model=List[schemas.Comment])
async def get_comments(db: Session = Depends(get_db)):
    comments = db.query(models.Comment).all()
    return comments

# Создание нового комментария
@app.post("/comments", response_model=schemas.Comment)
async def create_comment(comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    # Проверяем существование поста
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = models.Comment(
        content=comment.content,
        post_id=comment.post_id,
        user_id=1,  # Временно хардкодим user_id, позже будет авторизация
        created_at=datetime.utcnow()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# Получение избранного пользователя
@app.get("/favorites/{user_id}", response_model=List[schemas.Favorite])
async def get_favorites(user_id: int, db: Session = Depends(get_db)):
    favorites = db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()
    return favorites

# Добавление в избранное
@app.post("/favorites", response_model=schemas.Favorite)
async def add_to_favorites(favorite: schemas.FavoriteCreate, db: Session = Depends(get_db)):
    # Проверяем существование поста
    post = db.query(models.Post).filter(models.Post.id == favorite.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_favorite = models.Favorite(
        post_id=favorite.post_id,
        user_id=favorite.user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite 