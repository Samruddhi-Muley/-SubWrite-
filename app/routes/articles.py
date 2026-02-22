from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.utils.auth import get_current_writer

router = APIRouter(prefix="/api/articles", tags=["Articles API"])


@router.get("/", response_model=List[ArticleResponse])
def get_published_articles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    articles = db.query(Article).filter(Article.is_published == True).offset(skip).limit(limit).all()
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id, Article.is_published == True).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article(
        article: ArticleCreate,
        current_user: User = Depends(get_current_writer),
        db: Session = Depends(get_db)
):
    db_article = Article(**article.dict(), author_id=current_user.id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.get("/my/articles", response_model=List[ArticleResponse])
def get_my_articles(
        current_user: User = Depends(get_current_writer),
        db: Session = Depends(get_db)
):
    return db.query(Article).filter(Article.author_id == current_user.id).all()


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
        article_id: int,
        article_update: ArticleUpdate,
        current_user: User = Depends(get_current_writer),
        db: Session = Depends(get_db)
):
    db_article = db.query(Article).filter(
        Article.id == article_id,
        Article.author_id == current_user.id
    ).first()

    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    update_data = article_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_article, key, value)

    db.commit()
    db.refresh(db_article)
    return db_article


@router.delete("/{article_id}", status_code=204)
def delete_article(
        article_id: int,
        current_user: User = Depends(get_current_writer),
        db: Session = Depends(get_db)
):
    db_article = db.query(Article).filter(
        Article.id == article_id,
        Article.author_id == current_user.id
    ).first()

    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(db_article)
    db.commit()
    return None