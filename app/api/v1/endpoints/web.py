from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import (
    ADMIN_LOGIN_PATH,
    ACCESS_TOKEN_COOKIE,
    clear_access_token_cookie,
    get_user_from_access_token,
    require_html_user,
)
from app.core.templates import templates
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User

router = APIRouter(tags=["web"])


@router.get("/login", include_in_schema=False)
def legacy_login():
    return RedirectResponse(url=ADMIN_LOGIN_PATH, status_code=302)


@router.get("/dashboard", include_in_schema=False)
def legacy_dashboard():
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.get("/admin/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if token and get_user_from_access_token(token, db):
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    category_count = db.query(Category).count()
    active_category_count = db.query(Category).filter(Category.is_active.is_(True)).count()
    item_count = db.query(MenuItem).count()
    active_item_count = db.query(MenuItem).filter(MenuItem.is_active.is_(True)).count()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "category_count": category_count,
            "active_category_count": active_category_count,
            "item_count": item_count,
            "active_item_count": active_item_count,
        },
    )


@router.get("/admin/logout", include_in_schema=False)
def logout():
    response = RedirectResponse(url=ADMIN_LOGIN_PATH, status_code=302)
    clear_access_token_cookie(response)
    return response
