from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_html_user
from app.core.templates import templates
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User

router = APIRouter(tags=["admin-categories"])


def _checkbox_bool(value: str | None) -> bool:
    return value in ("1", "on", "true", "yes")


@router.get("/admin/categories", response_class=HTMLResponse, include_in_schema=False)
def list_categories(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    categories = (
        db.query(Category)
        .order_by(Category.display_order, Category.id)
        .all()
    )
    item_counts = dict(
        db.query(MenuItem.category_id, func.count(MenuItem.id))
        .group_by(MenuItem.category_id)
        .all()
    )
    return templates.TemplateResponse(
        "admin/categories/list.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "item_counts": item_counts,
        },
    )


@router.get("/admin/categories/new", response_class=HTMLResponse, include_in_schema=False)
def new_category_form(
    request: Request,
    user: User = Depends(require_html_user),
):
    return templates.TemplateResponse(
        "admin/categories/form.html",
        {
            "request": request,
            "user": user,
            "category": None,
            "form_action": "/admin/categories/new",
            "page_title": "New Category",
        },
    )


@router.post("/admin/categories/new", include_in_schema=False)
def create_category(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
    name_ar: str = Form(...),
    name_en: str = Form(...),
    note_ar: str = Form(""),
    note_en: str = Form(""),
    display_order: int = Form(0),
    is_active: str | None = Form(None),
):
    category = Category(
        name_ar=name_ar.strip(),
        name_en=name_en.strip(),
        note_ar=note_ar.strip() or None,
        note_en=note_en.strip() or None,
        display_order=display_order,
        is_active=_checkbox_bool(is_active),
    )
    db.add(category)
    db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.get(
    "/admin/categories/{category_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def edit_category_form(
    request: Request,
    category_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return RedirectResponse(url="/admin/categories", status_code=302)
    return templates.TemplateResponse(
        "admin/categories/form.html",
        {
            "request": request,
            "user": user,
            "category": category,
            "form_action": f"/admin/categories/{category_id}/edit",
            "page_title": "Edit Category",
        },
    )


@router.post("/admin/categories/{category_id}/edit", include_in_schema=False)
def update_category(
    category_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
    name_ar: str = Form(...),
    name_en: str = Form(...),
    note_ar: str = Form(""),
    note_en: str = Form(""),
    display_order: int = Form(0),
    is_active: str | None = Form(None),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return RedirectResponse(url="/admin/categories", status_code=302)
    category.name_ar = name_ar.strip()
    category.name_en = name_en.strip()
    category.note_ar = note_ar.strip() or None
    category.note_en = note_en.strip() or None
    category.display_order = display_order
    category.is_active = _checkbox_bool(is_active)
    db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)


@router.get(
    "/admin/categories/{category_id}/delete",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def delete_category_confirm(
    request: Request,
    category_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return RedirectResponse(url="/admin/categories", status_code=302)
    item_count = (
        db.query(MenuItem).filter(MenuItem.category_id == category_id).count()
    )
    if item_count == 0:
        db.delete(category)
        db.commit()
        return RedirectResponse(url="/admin/categories", status_code=303)
    return templates.TemplateResponse(
        "admin/categories/delete_confirm.html",
        {
            "request": request,
            "user": user,
            "category": category,
            "item_count": item_count,
        },
    )


@router.post("/admin/categories/{category_id}/delete", include_in_schema=False)
def delete_category(
    category_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
    confirm_delete: str | None = Form(None),
):
    from app.core.uploads import delete_upload

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        return RedirectResponse(url="/admin/categories", status_code=302)

    items = db.query(MenuItem).filter(MenuItem.category_id == category_id).all()
    if items and not _checkbox_bool(confirm_delete):
        return RedirectResponse(
            url=f"/admin/categories/{category_id}/delete",
            status_code=303,
        )

    for item in items:
        delete_upload(item.image_path)
        db.delete(item)
    db.delete(category)
    db.commit()
    return RedirectResponse(url="/admin/categories", status_code=303)
