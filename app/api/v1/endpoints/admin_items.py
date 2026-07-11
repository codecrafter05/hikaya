from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import require_html_user
from app.core.menu_prices import format_prices, parse_price_tiers
from app.core.templates import templates
from app.core.uploads import delete_upload, save_upload, upload_url
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.models.user import User

router = APIRouter(tags=["admin-items"])


def _checkbox_bool(value: str | None) -> bool:
    return value in ("1", "on", "true", "yes")


def _get_form_categories(db: Session, selected_id: int | None = None) -> list[Category]:
    categories = (
        db.query(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.display_order, Category.name_en)
        .all()
    )
    if selected_id and selected_id not in {c.id for c in categories}:
        current = db.query(Category).filter(Category.id == selected_id).first()
        if current:
            categories = [current] + categories
    return categories


def _form_data(
    *,
    category_id: int,
    name_ar: str,
    name_en: str,
    description_ar: str,
    description_en: str,
    display_order: int,
    is_active: bool,
    prices: list[dict],
) -> dict:
    return {
        "category_id": category_id,
        "name_ar": name_ar,
        "name_en": name_en,
        "description_ar": description_ar,
        "description_en": description_en,
        "display_order": display_order,
        "is_active": is_active,
        "prices": prices,
    }


@router.get("/admin/items", response_class=HTMLResponse, include_in_schema=False)
def list_items(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(MenuItem)
        .options(joinedload(MenuItem.category))
        .order_by(MenuItem.display_order, MenuItem.id)
        .all()
    )
    return templates.TemplateResponse(
        "admin/items/list.html",
        {
            "request": request,
            "user": user,
            "items": items,
            "format_prices": format_prices,
            "upload_url": upload_url,
        },
    )


@router.get("/admin/items/new", response_class=HTMLResponse, include_in_schema=False)
def new_item_form(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    categories = _get_form_categories(db)
    return templates.TemplateResponse(
        "admin/items/form.html",
        {
            "request": request,
            "user": user,
            "item": None,
            "categories": categories,
            "form_action": "/admin/items/new",
            "page_title": "New Menu Item",
            "upload_url": upload_url,
            "error": None,
        },
    )


@router.post("/admin/items/new", include_in_schema=False)
async def create_item(
    request: Request,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
    category_id: int = Form(...),
    name_ar: str = Form(...),
    name_en: str = Form(...),
    description_ar: str = Form(""),
    description_en: str = Form(""),
    display_order: int = Form(0),
    is_active: str | None = Form(None),
    price_label_ar: list[str] = Form(default=[]),
    price_label_en: list[str] = Form(default=[]),
    price_values: list[str] = Form(default=[]),
    image: UploadFile | None = File(None),
):
    categories = _get_form_categories(db, selected_id=category_id)
    prices, price_error = parse_price_tiers(price_label_ar, price_label_en, price_values)
    image_path = None
    error = price_error

    if error is None and db.query(Category).filter(Category.id == category_id).first() is None:
        error = "Please select a valid category."

    if error is None and image and image.filename:
        try:
            image_path = await save_upload(image)
        except ValueError as exc:
            error = str(exc)

    if error:
        return templates.TemplateResponse(
            "admin/items/form.html",
            {
                "request": request,
                "user": user,
                "item": None,
                "categories": categories,
                "form_action": "/admin/items/new",
                "page_title": "New Menu Item",
                "upload_url": upload_url,
                "error": error,
                "form_data": _form_data(
                    category_id=category_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    description_ar=description_ar,
                    description_en=description_en,
                    display_order=display_order,
                    is_active=_checkbox_bool(is_active),
                    prices=prices
                    or [
                        {
                            "label_ar": price_label_ar[i] if i < len(price_label_ar) else "",
                            "label_en": price_label_en[i] if i < len(price_label_en) else "",
                            "price": price_values[i] if i < len(price_values) else "",
                        }
                        for i in range(
                            max(len(price_label_ar), len(price_label_en), len(price_values))
                        )
                    ],
                ),
            },
            status_code=400,
        )

    item = MenuItem(
        category_id=category_id,
        name_ar=name_ar.strip(),
        name_en=name_en.strip(),
        description_ar=description_ar.strip() or None,
        description_en=description_en.strip() or None,
        image_path=image_path,
        prices=prices,
        display_order=display_order,
        is_active=_checkbox_bool(is_active),
    )
    db.add(item)
    db.commit()
    return RedirectResponse(url="/admin/items", status_code=303)


@router.get(
    "/admin/items/{item_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def edit_item_form(
    request: Request,
    item_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item is None:
        return RedirectResponse(url="/admin/items", status_code=302)
    categories = _get_form_categories(db, selected_id=item.category_id)
    return templates.TemplateResponse(
        "admin/items/form.html",
        {
            "request": request,
            "user": user,
            "item": item,
            "categories": categories,
            "form_action": f"/admin/items/{item_id}/edit",
            "page_title": "Edit Menu Item",
            "upload_url": upload_url,
            "error": None,
        },
    )


@router.post("/admin/items/{item_id}/edit", include_in_schema=False)
async def update_item(
    request: Request,
    item_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
    category_id: int = Form(...),
    name_ar: str = Form(...),
    name_en: str = Form(...),
    description_ar: str = Form(""),
    description_en: str = Form(""),
    display_order: int = Form(0),
    is_active: str | None = Form(None),
    price_label_ar: list[str] = Form(default=[]),
    price_label_en: list[str] = Form(default=[]),
    price_values: list[str] = Form(default=[]),
    image: UploadFile | None = File(None),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item is None:
        return RedirectResponse(url="/admin/items", status_code=302)

    categories = _get_form_categories(db, selected_id=category_id)
    prices, price_error = parse_price_tiers(price_label_ar, price_label_en, price_values)
    error = price_error

    if error is None and db.query(Category).filter(Category.id == category_id).first() is None:
        error = "Please select a valid category."

    old_image_path = item.image_path
    new_image_path = old_image_path

    if error is None and image and image.filename:
        try:
            new_image_path = await save_upload(image)
        except ValueError as exc:
            error = str(exc)

    if error:
        return templates.TemplateResponse(
            "admin/items/form.html",
            {
                "request": request,
                "user": user,
                "item": item,
                "categories": categories,
                "form_action": f"/admin/items/{item_id}/edit",
                "page_title": "Edit Menu Item",
                "upload_url": upload_url,
                "error": error,
                "form_data": _form_data(
                    category_id=category_id,
                    name_ar=name_ar,
                    name_en=name_en,
                    description_ar=description_ar,
                    description_en=description_en,
                    display_order=display_order,
                    is_active=_checkbox_bool(is_active),
                    prices=prices
                    or [
                        {
                            "label_ar": price_label_ar[i] if i < len(price_label_ar) else "",
                            "label_en": price_label_en[i] if i < len(price_label_en) else "",
                            "price": price_values[i] if i < len(price_values) else "",
                        }
                        for i in range(
                            max(len(price_label_ar), len(price_label_en), len(price_values))
                        )
                    ],
                ),
            },
            status_code=400,
        )

    item.category_id = category_id
    item.name_ar = name_ar.strip()
    item.name_en = name_en.strip()
    item.description_ar = description_ar.strip() or None
    item.description_en = description_en.strip() or None
    item.prices = prices
    item.display_order = display_order
    item.is_active = _checkbox_bool(is_active)

    if new_image_path != old_image_path:
        item.image_path = new_image_path
        db.commit()
        delete_upload(old_image_path)
    else:
        db.commit()

    return RedirectResponse(url="/admin/items", status_code=303)


@router.post("/admin/items/{item_id}/delete", include_in_schema=False)
def delete_item(
    item_id: int,
    user: User = Depends(require_html_user),
    db: Session = Depends(get_db),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if item is None:
        return RedirectResponse(url="/admin/items", status_code=302)
    delete_upload(item.image_path)
    db.delete(item)
    db.commit()
    return RedirectResponse(url="/admin/items", status_code=303)
