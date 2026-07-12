"""
Load the real Hikaya menu (4 categories, 37 items).

One-time data load — wraps inserts in a transaction (rollback on error).
Does NOT touch users or admin credentials.
Does NOT wipe existing data — wipe separately before running if needed.

Usage (from project root):
    .venv/bin/python scripts/seed_real_menu.py
"""
from __future__ import annotations

import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.core.database import SessionLocal
from app.models.category import Category
from app.models.menu_item import MenuItem

MILK_SWEETNESS = [
    {
        "group_ar": "نوع الحليب",
        "group_en": "Milk type",
        "required": True,
        "choices": [
            {"label_ar": "كامل الدسم", "label_en": "Whole", "price_delta": 0.0},
            {"label_ar": "خالي الدسم", "label_en": "Skimmed", "price_delta": 0.0},
            {"label_ar": "شوفان", "label_en": "Oat", "price_delta": 0.3},
            {"label_ar": "لوز", "label_en": "Almond", "price_delta": 0.0},
        ],
    },
    {
        "group_ar": "درجة التحلية",
        "group_en": "Sweetness",
        "required": True,
        "choices": [
            {"label_ar": "عادي", "label_en": "Regular", "price_delta": 0.0},
            {"label_ar": "أقل", "label_en": "Less", "price_delta": 0.0},
            {"label_ar": "زيادة", "label_en": "More", "price_delta": 0.0},
        ],
    },
]

BEAN_TYPE = [
    {
        "group_ar": "نوع البن",
        "group_en": "Coffee bean type",
        "required": True,
        "choices": [
            {"label_ar": "كولومبي", "label_en": "Colombian", "price_delta": 0.0},
            {"label_ar": "برازيلي", "label_en": "Brazilian", "price_delta": 0.0},
            {"label_ar": "إثيوبي", "label_en": "Ethiopian", "price_delta": 0.0},
        ],
    },
]

NONE: list = []

CATEGORIES = [
    {
        "name_en": "Hot Drinks",
        "name_ar": "مشروبات ساخنة",
        "display_order": 1,
        "note_en": "Pickup only",
        "note_ar": "استلام من الفرع",
    },
    {
        "name_en": "Cold Drinks",
        "name_ar": "مشروبات باردة",
        "display_order": 2,
        "note_en": "Pickup only",
        "note_ar": "استلام من الفرع",
    },
    {
        "name_en": "Desserts",
        "name_ar": "حلويات",
        "display_order": 3,
        "note_en": "Pickup only",
        "note_ar": "استلام من الفرع",
    },
    {
        "name_en": "Whole Cakes",
        "name_ar": "كيك كامل",
        "display_order": 4,
        "note_en": "Delivery only",
        "note_ar": "دليفري فقط",
    },
]

# (category_en, display_order, name_en, name_ar, price, option_groups_key)
ITEMS = [
    # Hot Drinks
    ("Hot Drinks", 1, "Hot Chocolate", "هوت شوكولت", 1.2, "milk"),
    ("Hot Drinks", 2, "Hot V60", "هوت V60", 1.6, "bean"),
    ("Hot Drinks", 3, "Double Espresso", "دبل إسبريسو", 1.2, "none"),
    ("Hot Drinks", 4, "Macchiato", "ماكياتو", 1.3, "none"),
    ("Hot Drinks", 5, "Cortado", "كورتادو", 1.3, "none"),
    ("Hot Drinks", 6, "Hot Americano", "هوت أمريكانو", 1.4, "none"),
    ("Hot Drinks", 7, "Cappuccino", "كابتشينو", 1.5, "milk"),
    ("Hot Drinks", 8, "Flat White", "فلات وايت", 1.5, "milk"),
    ("Hot Drinks", 9, "Coffee Latte", "كوفي لاتيه", 1.6, "milk"),
    ("Hot Drinks", 10, "Spanish Latte", "سبانيش لاتيه", 1.6, "milk"),
    ("Hot Drinks", 11, "White Mocha Latte", "وايت موكا لاتيه", 1.6, "milk"),
    ("Hot Drinks", 12, "Salted Caramel", "سولتد كراميل", 1.6, "milk"),
    ("Hot Drinks", 13, "Caramel Latte", "كراميل لاتيه", 1.6, "milk"),
    ("Hot Drinks", 14, "Vanilla Latte", "فانيلا لاتيه", 1.6, "milk"),
    ("Hot Drinks", 15, "Hikaya Signature (Hot)", "سيجنتشر حكاية (ساخن)", 2.0, "milk"),
    # Cold Drinks
    ("Cold Drinks", 1, "Signature Hikaya Café", "سيجنتشر حكاية كافيه", 2.0, "milk"),
    ("Cold Drinks", 2, "Iced White Mocha Latte", "آيسد وايت موكا لاتيه", 1.6, "milk"),
    ("Cold Drinks", 3, "Ice Salted Caramel", "آيس سولتد كراميل", 1.6, "milk"),
    ("Cold Drinks", 4, "Ice Vanilla Latte", "آيس فانيلا لاتيه", 1.6, "milk"),
    ("Cold Drinks", 5, "Ice Caramel Latte", "آيس كراميل لاتيه", 1.6, "milk"),
    ("Cold Drinks", 6, "Iced Latte", "آيسد لاتيه", 1.6, "milk"),
    ("Cold Drinks", 7, "Iced Spanish Latte", "آيسد سبانيش لاتيه", 1.6, "milk"),
    ("Cold Drinks", 8, "Iced Americano", "آيسد أمريكانو", 1.4, "none"),
    ("Cold Drinks", 9, "Iced V60", "آيسد V60", 1.6, "bean"),
    ("Cold Drinks", 10, "Strawberry Matcha", "ماتشا فراولة", 1.8, "milk"),
    ("Cold Drinks", 11, "Vanilla Matcha", "ماتشا فانيلا", 1.8, "milk"),
    ("Cold Drinks", 12, "Matcha Cloud Latte", "ماتشا كلاود لاتيه", 2.0, "milk"),
    ("Cold Drinks", 13, "Mojito – Strawberry", "موهيتو فراولة", 1.2, "none"),
    ("Cold Drinks", 14, "Mojito – Blue Lagoon", "موهيتو بلو لاجون", 1.2, "none"),
    ("Cold Drinks", 15, "Mojito – Lemon Mint", "موهيتو ليمون نعناع", 1.2, "none"),
    ("Cold Drinks", 16, "Mojito – Passion Fruit", "موهيتو باشن فروت", 1.2, "none"),
    ("Cold Drinks", 17, "Peach Iced Tea", "شاي مثلج بالخوخ", 1.5, "none"),
    # Desserts
    ("Desserts", 1, "Hikaya Cookies", "كوكيز حكاية", 1.2, "none"),
    ("Desserts", 2, "Muharraq Nights Cookies", "كوكيز ليالي المحرق", 1.2, "none"),
    ("Desserts", 3, "London Cake (Slice)", "لندن كيك (قطعة)", 2.5, "none"),
    # Whole Cakes
    ("Whole Cakes", 1, "London Cake (Whole)", "لندن كيك (كامل)", 17.0, "none"),
    ("Whole Cakes", 2, "Sansabistain Cake (Whole)", "سان سباستيان كيك (كامل)", 18.0, "none"),
]


def option_groups_for(key: str) -> list:
    if key == "milk":
        return copy.deepcopy(MILK_SWEETNESS)
    if key == "bean":
        return copy.deepcopy(BEAN_TYPE)
    return copy.deepcopy(NONE)


def price_tiers(price: float) -> list[dict]:
    return [{"label_ar": "السعر", "label_en": "Price", "price": float(f"{price:.3f}")}]


def main() -> None:
    if len(ITEMS) != 37:
        print(f"ERROR: expected 37 items, got {len(ITEMS)}", file=sys.stderr)
        sys.exit(1)
    if len(CATEGORIES) != 4:
        print(f"ERROR: expected 4 categories, got {len(CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        category_by_en: dict[str, Category] = {}
        for cat_data in CATEGORIES:
            category = Category(
                name_en=cat_data["name_en"],
                name_ar=cat_data["name_ar"],
                note_en=cat_data["note_en"],
                note_ar=cat_data["note_ar"],
                display_order=cat_data["display_order"],
                is_active=True,
            )
            db.add(category)
            db.flush()
            category_by_en[cat_data["name_en"]] = category
            print(
                f"CREATE category: {category.name_en} "
                f"(id={category.id}, note_en={category.note_en})"
            )

        for category_en, display_order, name_en, name_ar, price, opt_key in ITEMS:
            category = category_by_en[category_en]
            item = MenuItem(
                category_id=category.id,
                name_en=name_en,
                name_ar=name_ar,
                description_ar=None,
                description_en=None,
                image_path=None,
                prices=price_tiers(price),
                option_groups=option_groups_for(opt_key),
                display_order=display_order,
                is_active=True,
            )
            db.add(item)
            db.flush()
            print(
                f"CREATE item: {item.name_en} "
                f"(id={item.id}, cat={category_en}, "
                f"price={price:.3f}, options={opt_key})"
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    db = SessionLocal()
    try:
        cat_count = db.query(Category).count()
        item_count = db.query(MenuItem).count()
    finally:
        db.close()

    print()
    print("=== Real menu seed complete ===")
    print(f"Categories: {cat_count}")
    print(f"Items:      {item_count}")


if __name__ == "__main__":
    main()
