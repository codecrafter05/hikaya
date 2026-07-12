import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.templates import templates
from app.core.uploads import upload_url
from app.models.category import Category
from app.models.menu_item import MenuItem

router = APIRouter(tags=["public-menu"])


def _build_menu_payload(db: Session) -> dict:
    categories = (
        db.query(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.display_order, Category.id)
        .all()
    )
    category_ids = [c.id for c in categories]
    items_by_category: dict[int, list[dict]] = {cid: [] for cid in category_ids}

    if category_ids:
        items = (
            db.query(MenuItem)
            .filter(
                MenuItem.category_id.in_(category_ids),
                MenuItem.is_active.is_(True),
            )
            .order_by(MenuItem.display_order, MenuItem.id)
            .all()
        )
        for item in items:
            items_by_category[item.category_id].append(
                {
                    "id": item.id,
                    "name_ar": item.name_ar,
                    "name_en": item.name_en,
                    "description_ar": item.description_ar or "",
                    "description_en": item.description_en or "",
                    "image_url": upload_url(item.image_path),
                    "prices": item.prices or [],
                    "option_groups": item.option_groups or [],
                }
            )

    return {
        "categories": [
            {
                "id": category.id,
                "name_ar": category.name_ar,
                "name_en": category.name_en,
                "note_ar": category.note_ar or "",
                "note_en": category.note_en or "",
                "items": items_by_category.get(category.id, []),
            }
            for category in categories
            if items_by_category.get(category.id)
        ],
        "whatsapp_number": settings.WHATSAPP_NUMBER,
        "currency_label": settings.CURRENCY_LABEL,
    }


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def public_menu(request: Request, db: Session = Depends(get_db)):
    menu_data = _build_menu_payload(db)
    return templates.TemplateResponse(
        "public/menu.html",
        {
            "request": request,
            "menu_json": json.dumps(menu_data, ensure_ascii=False),
            "whatsapp_number": settings.WHATSAPP_NUMBER,
            "currency_label": settings.CURRENCY_LABEL,
        },
    )
