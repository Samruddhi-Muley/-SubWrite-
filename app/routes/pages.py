from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.article import Article
from app.models.user import User
from app.utils.auth import (
    get_current_user_optional,
    get_password_hash,
    verify_password,
    create_access_token
)
from datetime import timedelta
from typing import Optional
from app.utils.markdown_helper import render_markdown
from app.utils.email import send_welcome_email, send_verification_email
import secrets
from datetime import datetime, timedelta
from app.utils.email import send_password_reset_email
from app.models.like import Like
from app.models.follow import Follow
from app.models.comment import Comment

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="app/templates")

# Register markdown filter
templates.env.filters['markdown'] = render_markdown


@router.get("/", response_class=HTMLResponse)
async def home(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    articles = db.query(Article).filter(
        Article.is_published == True
    ).order_by(Article.created_at.desc()).all()

    # Get like counts and comment counts for all articles
    article_likes_count = {}
    article_comments_count = {}

    for article in articles:
        # Count likes
        like_count = db.query(Like).filter(Like.article_id == article.id).count()
        article_likes_count[article.id] = like_count

        # Count comments
        comment_count = db.query(Comment).filter(Comment.article_id == article.id).count()
        article_comments_count[article.id] = comment_count

    return templates.TemplateResponse("home.html", {
        "request": request,
        "articles": articles,
        "article_likes_count": article_likes_count,
        "article_comments_count": article_comments_count,  # Make sure this is here!
        "current_user": current_user
    })


@router.get("/article/{article_id}", response_class=HTMLResponse)
async def article_detail(
        article_id: int,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    article = db.query(Article).filter(
        Article.id == article_id,
        Article.is_published == True
    ).first()

    if not article:
        return HTMLResponse("<h1>Article not found</h1>", status_code=404)

    # Get likes for this article
    article_likes = db.query(Like).filter(Like.article_id == article_id).all()

    # Get comments for this article
    comments = db.query(Comment).filter(Comment.article_id == article_id).order_by(Comment.created_at.asc()).all()

    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
        "article_likes": article_likes,
        "comments": comments,  # ← Make sure this line is here!
        "current_user": current_user
    })

# LOGIN PAGES
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": None,
        "error": None
    })


@router.post("/login", response_class=HTMLResponse)
async def login_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "current_user": None,
            "error": "Invalid username or password"
        }, status_code=400)

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=1)
    )

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response


# REGISTER PAGES
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "current_user": None,
        "error": None
    })


@router.post("/register", response_class=HTMLResponse)
async def register_form(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        full_name: Optional[str] = Form(None),
        is_writer: Optional[str] = Form(None),
        db: Session = Depends(get_db)
):
    # Check if user exists
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "error": "Username or email already exists"
        }, status_code=400)

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)

    # Create user
    db_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        is_writer=(is_writer == "true"),
        verification_token=verification_token  # NEW: Save token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send welcome email (runs in background - doesn't block)
    try:
        send_welcome_email(email, username)
        send_verification_email(email, username, verification_token)
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Don't fail registration if email fails

    # Auto-login
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(days=1)
    )

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    return response

# WRITER DASHBOARD
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_optional)):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    articles = db.query(Article).filter(Article.author_id == current_user.id).order_by(Article.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "articles": articles,
        "current_user": current_user
    })


@router.get("/write", response_class=HTMLResponse)
async def write_page(request: Request, current_user: User = Depends(get_current_user_optional)):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("write.html", {
        "request": request,
        "current_user": current_user,
        "article": None
    })


@router.get("/edit/{article_id}", response_class=HTMLResponse)
async def edit_page(article_id: int, request: Request, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user_optional)):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    article = db.query(Article).filter(
        Article.id == article_id,
        Article.author_id == current_user.id
    ).first()

    if not article:
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse("write.html", {
        "request": request,
        "current_user": current_user,
        "article": article
    })

@router.post("/create-article", response_class=HTMLResponse)
async def create_article_form(
        request: Request,
        title: str = Form(...),
        subtitle: Optional[str] = Form(None),
        content: str = Form(...),
        tags: Optional[str] = Form(None),  # NEW: Add tags
        is_published: Optional[str] = Form(None),
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    # Create article
    db_article = Article(
        title=title,
        subtitle=subtitle,
        content=content,
        tags=tags,  # NEW: Save tags
        is_published=(is_published == "on"),
        author_id=current_user.id
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    return RedirectResponse(url="/dashboard", status_code=302)


@router.post("/update-article/{article_id}", response_class=HTMLResponse)
async def update_article_form(
        article_id: int,
        request: Request,
        title: str = Form(...),
        subtitle: Optional[str] = Form(None),
        content: str = Form(...),
        tags: Optional[str] = Form(None),  # NEW: Add tags
        is_published: Optional[str] = Form(None),
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    db_article = db.query(Article).filter(
        Article.id == article_id,
        Article.author_id == current_user.id
    ).first()

    if not db_article:
        return RedirectResponse(url="/dashboard", status_code=302)

    # Update article
    db_article.title = title
    db_article.subtitle = subtitle
    db_article.content = content
    db_article.tags = tags  # NEW: Update tags
    db_article.is_published = (is_published == "on")

    db.commit()
    db.refresh(db_article)

    return RedirectResponse(url="/dashboard", status_code=302)
@router.post("/delete-article/{article_id}")
async def delete_article_form(
        article_id: int,
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user or not current_user.is_writer:
        return RedirectResponse(url="/login", status_code=302)

    db_article = db.query(Article).filter(
        Article.id == article_id,
        Article.author_id == current_user.id
    ).first()

    if db_article:
        db.delete(db_article)
        db.commit()

    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/profile/{username}", response_class=HTMLResponse)
async def user_profile(
        username: str,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    # Get the profile user
    profile_user = db.query(User).filter(User.username == username).first()
    if not profile_user:
        return HTMLResponse("<h1>User not found</h1>", status_code=404)

    # Get published articles by this user
    articles = db.query(Article).filter(
        Article.author_id == profile_user.id,
        Article.is_published == True
    ).order_by(Article.created_at.desc()).all()

    # Get follower/following counts
    followers_count = db.query(Follow).filter(Follow.following_id == profile_user.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == profile_user.id).count()

    # Check if current user is following this profile
    is_following = False
    if current_user:
        is_following = db.query(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.following_id == profile_user.id
        ).first() is not None

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": profile_user,
        "articles": articles,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "current_user": current_user
    })

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
        request: Request,
        current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": current_user,
        "success": False
    })


@router.post("/update-profile", response_class=HTMLResponse)
async def update_profile(
        request: Request,
        full_name: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        profile_image: Optional[str] = Form(None),
        website_url: Optional[str] = Form(None),
        twitter_url: Optional[str] = Form(None),
        github_url: Optional[str] = Form(None),
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Update user profile
    if full_name is not None:
        current_user.full_name = full_name
    if bio is not None:
        current_user.bio = bio[:500]  # Limit to 500 characters
    if profile_image:
        current_user.profile_image = profile_image
    if website_url:
        current_user.website_url = website_url
    if twitter_url:
        current_user.twitter_url = twitter_url
    if github_url:
        current_user.github_url = github_url

    db.commit()
    db.refresh(current_user)

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "current_user": current_user,
        "success": True
    })


@router.get("/tag/{tag_name}", response_class=HTMLResponse)
async def tag_page(
        tag_name: str,
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    # Find all published articles with this tag
    articles = db.query(Article).filter(
        Article.is_published == True,
        Article.tags.like(f'%{tag_name}%')
    ).order_by(Article.created_at.desc()).all()

    # Filter to exact tag matches (in case of partial matches)
    filtered_articles = [
        article for article in articles
        if tag_name in article.get_tags_list()
    ]

    return templates.TemplateResponse("tag.html", {
        "request": request,
        "tag_name": tag_name,
        "articles": filtered_articles,
        "current_user": current_user
    })


@router.get("/tags", response_class=HTMLResponse)
async def all_tags_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    # Get all published articles with tags
    articles = db.query(Article).filter(
        Article.is_published == True,
        Article.tags.isnot(None)
    ).all()

    # Count articles per tag
    tag_counts = {}
    for article in articles:
        for tag in article.get_tags_list():
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count (descending)
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return templates.TemplateResponse("tags.html", {
        "request": request,
        "tags": sorted_tags,
        "current_user": current_user
    })


@router.get("/search", response_class=HTMLResponse)
async def search_page(
        request: Request,
        q: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    results = []

    if q:
        search_term = f"%{q}%"

        # Search in title, content, subtitle, and author username
        results = db.query(Article).join(User).filter(
            Article.is_published == True,
            or_(
                Article.title.like(search_term),
                Article.subtitle.like(search_term),
                Article.content.like(search_term),
                User.username.like(search_term),
                Article.tags.like(search_term)
            )
        ).order_by(Article.created_at.desc()).all()

    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q or "",
        "results": results,
        "current_user": current_user
    })


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email(
        request: Request,
        token: str,
        db: Session = Depends(get_db)
):
    # Find user with this verification token
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        return templates.TemplateResponse("verify_error.html", {
            "request": request,
            "current_user": None,
            "message": "Invalid verification link. This link may have expired or been used already."
        })

    # Check if already verified
    if user.is_verified:
        return templates.TemplateResponse("verify_success.html", {
            "request": request,
            "current_user": None,
            "message": "Your email is already verified! You can login now.",
            "already_verified": True
        })

    # Verify the user
    user.is_verified = True
    user.verification_token = None  # Clear the token
    db.commit()

    return templates.TemplateResponse("verify_success.html", {
        "request": request,
        "current_user": None,
        "message": "Email verified successfully! You can now enjoy all features of SubWrite.",
        "already_verified": False
    })


# Forgot Password - Show form
@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "error": None,
        "success": None
    })


# Forgot Password - Handle form submission
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(
        request: Request,
        email: str = Form(...),
        db: Session = Depends(get_db)
):
    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Don't reveal if email exists (security)
        return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "error": None,
            "success": "If that email exists, we've sent a password reset link."
        })

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)  # Expires in 1 hour

    # Save token to database
    user.reset_token = reset_token
    user.reset_token_expires = reset_expires
    db.commit()

    # Send reset email
    try:
        send_password_reset_email(email, user.username, reset_token)
    except Exception as e:
        print(f"Failed to send reset email: {e}")

    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
        "error": None,
        "success": "If that email exists, we've sent a password reset link. Please check your inbox."
    })


# Reset Password - Show form (from email link)
@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(
        request: Request,
        token: str,
        db: Session = Depends(get_db)
):
    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        return templates.TemplateResponse("verify_error.html", {
            "request": request,
            "current_user": None,
            "message": "Invalid or expired reset link."
        })

    # Check if token expired
    if user.reset_token_expires < datetime.utcnow():
        return templates.TemplateResponse("verify_error.html", {
            "request": request,
            "current_user": None,
            "message": "This reset link has expired. Please request a new one."
        })

    return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "token": token,
        "error": None
    })


# Reset Password - Handle form submission
@router.post("/reset-password", response_class=HTMLResponse)
async def reset_password_submit(
        request: Request,
        token: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    # Check passwords match
    if password != confirm_password:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "token": token,
            "error": "Passwords do not match."
        })

    # Find user with this reset token
    user = db.query(User).filter(User.reset_token == token).first()

    if not user or user.reset_token_expires < datetime.utcnow():
        return templates.TemplateResponse("verify_error.html", {
            "request": request,
            "current_user": None,
            "message": "Invalid or expired reset link."
        })

    # Update password
    user.hashed_password = get_password_hash(password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return templates.TemplateResponse("reset_success.html", {
        "request": request
    })


# Like/Unlike Article
@router.post("/like/{article_id}")
async def like_article(
        article_id: int,
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Check if article exists
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return RedirectResponse(url="/", status_code=302)

    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.article_id == article_id
    ).first()

    if existing_like:
        # Unlike - remove the like
        db.delete(existing_like)
        db.commit()
    else:
        # Like - add new like
        new_like = Like(user_id=current_user.id, article_id=article_id)
        db.add(new_like)
        db.commit()

    # Redirect back to article
    return RedirectResponse(url=f"/article/{article_id}", status_code=302)


# Add Comment
@router.post("/comment/{article_id}")
async def add_comment(
        article_id: int,
        content: str = Form(...),
        parent_id: Optional[int] = Form(None),
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Create comment
    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        article_id=article_id,
        parent_id=parent_id
    )
    db.add(new_comment)
    db.commit()

    return RedirectResponse(url=f"/article/{article_id}#comments", status_code=302)


# Follow/Unfollow User
@router.post("/follow/{username}")
async def follow_user(
        username: str,
        current_user: User = Depends(get_current_user_optional),
        db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Find user to follow
    user_to_follow = db.query(User).filter(User.username == username).first()
    if not user_to_follow or user_to_follow.id == current_user.id:
        return RedirectResponse(url="/", status_code=302)

    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.following_id == user_to_follow.id
    ).first()

    if existing_follow:
        # Unfollow
        db.delete(existing_follow)
        db.commit()
    else:
        # Follow
        new_follow = Follow(
            follower_id=current_user.id,
            following_id=user_to_follow.id
        )
        db.add(new_follow)
        db.commit()

    return RedirectResponse(url=f"/profile/{username}", status_code=302)


# My Feed Page
@router.get("/feed", response_class=HTMLResponse)
async def feed_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Get users that current user follows
    following = db.query(Follow).filter(Follow.follower_id == current_user.id).all()
    following_ids = [f.following_id for f in following]

    # Get articles from followed users
    articles = []
    if following_ids:
        articles = db.query(Article).filter(
            Article.author_id.in_(following_ids),
            Article.is_published == True
        ).order_by(Article.created_at.desc()).all()

    return templates.TemplateResponse("feed.html", {
        "request": request,
        "articles": articles,
        "current_user": current_user
    })

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response