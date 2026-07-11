"""
Seed demo categories & menu items from static/public/img/.

Idempotent: safe to re-run (skips existing name_en).
Does NOT touch users or unrelated data.

Usage (from project root):
    .venv/bin/python scripts/seed_demo_menu.py
"""
from __future__ import annotations

import os
import shutil
import sys
import uuid
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.core.database import SessionLocal
from app.core.uploads import UPLOAD_DIR, ensure_upload_dir
from app.models.category import Category
from app.models.menu_item import MenuItem

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = PROJECT_ROOT / "static" / "public" / "img"

# NOTE: All names/descriptions below are PLACEHOLDER demo content for testing.
# Replace with real menu copy before client handoff.

CATEGORIES = [
    {
        "name_en": "Hot Drinks",
        "name_ar": "مشروبات ساخنة",
        "display_order": 1,
    },
    {
        "name_en": "Cold Drinks",
        "name_ar": "مشروبات باردة",
        "display_order": 2,
    },
    {
        "name_en": "Breakfast",
        "name_ar": "إفطار",
        "display_order": 3,
    },
    {
        "name_en": "Desserts",
        "name_ar": "حلويات",
        "display_order": 4,
    },
]

# image filenames from static/public/img/ (must exist on disk)
ITEMS = [
    # Hot Drinks
    {
        "category_en": "Hot Drinks",
        "name_en": "Classic Latte",
        "name_ar": "لاتيه كلاسيك",
        "description_en": "Smooth espresso with steamed milk and latte art.",
        "description_ar": "إسبريسو ناعم مع حليب مبخر وفن لاتيه.",
        "image": "02kim-latte-art-2431160_1920.jpg",
        "prices": [
            {"label_ar": "صغير", "label_en": "Small", "price": 1.5},
            {"label_ar": "وسط", "label_en": "Medium", "price": 1.8},
            {"label_ar": "كبير", "label_en": "Large", "price": 2.2},
        ],
        "display_order": 1,
    },
    {
        "category_en": "Hot Drinks",
        "name_en": "Cafe Latte Glass",
        "name_ar": "لاتيه كوب زجاج",
        "description_en": "Creamy latte served in a tall glass.",
        "description_ar": "لاتيه كريمي يقدم في كوب زجاجي طويل.",
        "image": "ssun39-cafe-latte-1823066_1920.jpg",
        "prices": [
            {"label_ar": "عادي", "label_en": "Regular", "price": 1.7},
            {"label_ar": "كبير", "label_en": "Large", "price": 2.0},
        ],
        "display_order": 2,
    },
    {
        "category_en": "Hot Drinks",
        "name_en": "Espresso Cup",
        "name_ar": "إسبريسو",
        "description_en": "Rich espresso shot with a warm café finish.",
        "description_ar": "جرعة إسبريسو غنية بطعم القهوة الدافئ.",
        "image": "pasrasaa-coffee-1582555_1920.jpg",
        "prices": [
            {"label_ar": "سنقل", "label_en": "Single", "price": 1.2},
            {"label_ar": "دبل", "label_en": "Double", "price": 1.6},
        ],
        "display_order": 3,
    },
    {
        "category_en": "Hot Drinks",
        "name_en": "House Coffee",
        "name_ar": "قهوة المنزل",
        "description_en": "Daily brew with a smooth, balanced taste.",
        "description_ar": "قهوة يومية بطعم متوازن وناعم.",
        "image": "pexels-coffee-1281752_1920.jpg",
        "prices": [
            {"label_ar": "كوب", "label_en": "Cup", "price": 1.3},
            {"label_ar": "كبير", "label_en": "Large", "price": 1.7},
        ],
        "display_order": 4,
    },
    {
        "category_en": "Hot Drinks",
        "name_en": "Barista Pour Over",
        "name_ar": "قهوة مصبوبة",
        "description_en": "Hand-poured coffee prepared fresh by the barista.",
        "description_ar": "قهوة مصبوبة يدوياً طازجة من الباريستا.",
        "image": "shixugang-coffee-563797.jpg",
        "prices": [
            {"label_ar": "كوب", "label_en": "Cup", "price": 1.9},
        ],
        "display_order": 5,
    },
    # Cold Drinks (reuse coffee images for demo)
    {
        "category_en": "Cold Drinks",
        "name_en": "Iced Latte",
        "name_ar": "آيس لاتيه",
        "description_en": "Chilled latte over ice — demo placeholder item.",
        "description_ar": "لاتيه مثلج — عنصر تجريبي للتجربة.",
        "image": "konradjanik-coffee-5176961.jpg",
        "prices": [
            {"label_ar": "وسط", "label_en": "Medium", "price": 1.9},
            {"label_ar": "كبير", "label_en": "Large", "price": 2.3},
        ],
        "display_order": 1,
    },
    {
        "category_en": "Cold Drinks",
        "name_en": "Iced Americano",
        "name_ar": "آيس أمريكانو",
        "description_en": "Espresso over cold water and ice.",
        "description_ar": "إسبريسو مع ماء بارد وثلج.",
        "image": "pexels-coffee-1281752_1920.jpg",
        "prices": [
            {"label_ar": "وسط", "label_en": "Medium", "price": 1.5},
            {"label_ar": "كبير", "label_en": "Large", "price": 1.8},
        ],
        "display_order": 2,
    },
    {
        "category_en": "Cold Drinks",
        "name_en": "Cold Brew",
        "name_ar": "كولد برو",
        "description_en": "Slow-steeped cold brew with a smooth finish.",
        "description_ar": "كولد برو منقوع ببطء بطعم ناعم.",
        "image": "pasrasaa-coffee-1582555_1920.jpg",
        "prices": [
            {"label_ar": "كوب", "label_en": "Cup", "price": 2.0},
            {"label_ar": "كبير", "label_en": "Large", "price": 2.4},
        ],
        "display_order": 3,
    },
    {
        "category_en": "Cold Drinks",
        "name_en": "Vanilla Iced Latte",
        "name_ar": "آيس لاتيه فانيلا",
        "description_en": "Iced latte with a light vanilla note.",
        "description_ar": "آيس لاتيه بنكهة فانيلا خفيفة.",
        "image": "ssun39-cafe-latte-1823066_1920.jpg",
        "prices": [
            {"label_ar": "وسط", "label_en": "Medium", "price": 2.1},
            {"label_ar": "كبير", "label_en": "Large", "price": 2.5},
        ],
        "display_order": 4,
    },
    # Breakfast
    {
        "category_en": "Breakfast",
        "name_en": "Chocolate Walnut Pancakes",
        "name_ar": "بانكيك شوكولاتة وجوز",
        "description_en": "Fluffy pancakes with chocolate, cream, coconut and walnuts.",
        "description_ar": "بانكيك هش مع شوكولاتة وكريمة وجوز هند وجوز.",
        "image": "sklostudio-pancakes-5989136_1920.jpg",
        "prices": [
            {"label_ar": "طبق", "label_en": "Plate", "price": 3.2},
            {"label_ar": "مع قهوة", "label_en": "With coffee", "price": 4.5},
        ],
        "display_order": 1,
    },
    {
        "category_en": "Breakfast",
        "name_en": "Pancake Breakfast Combo",
        "name_ar": "كومبو إفطار بانكيك",
        "description_en": "Pancake stack paired with a hot coffee — demo combo.",
        "description_ar": "طبق بانكيك مع قهوة ساخنة — كومبو تجريبي.",
        "image": "sklostudio-pancakes-5989136_1920.jpg",
        "prices": [
            {"label_ar": "كومبو", "label_en": "Combo", "price": 4.8},
        ],
        "display_order": 2,
    },
    {
        "category_en": "Breakfast",
        "name_en": "Morning Latte",
        "name_ar": "لاتيه الصباح",
        "description_en": "A morning latte to start the day.",
        "description_ar": "لاتيه الصباح لبداية اليوم.",
        "image": "02kim-latte-art-2431160_1920.jpg",
        "prices": [
            {"label_ar": "كوب", "label_en": "Cup", "price": 1.8},
        ],
        "display_order": 3,
    },
    {
        "category_en": "Breakfast",
        "name_en": "Breakfast Coffee",
        "name_ar": "قهوة الإفطار",
        "description_en": "Simple hot coffee for breakfast time.",
        "description_ar": "قهوة ساخنة بسيطة لوقت الإفطار.",
        "image": "konradjanik-coffee-5176961.jpg",
        "prices": [
            {"label_ar": "كوب", "label_en": "Cup", "price": 1.4},
            {"label_ar": "كبير", "label_en": "Large", "price": 1.8},
        ],
        "display_order": 4,
    },
    # Desserts
    {
        "category_en": "Desserts",
        "name_en": "Chocolate Macarons",
        "name_ar": "ماكرون الشوكولاتة",
        "description_en": "Delicate chocolate macarons with creamy ganache.",
        "description_ar": "ماكرون شوكولاتة رقيق مع حشوة الجاناش.",
        "image": "24457758-sweets-6851675_1920.jpg",
        "prices": [
            {"label_ar": "قطعتان", "label_en": "2 pieces", "price": 1.8},
            {"label_ar": "أربع قطع", "label_en": "4 pieces", "price": 3.2},
        ],
        "display_order": 1,
    },
    {
        "category_en": "Desserts",
        "name_en": "Sweet Macaron Box",
        "name_ar": "بوكس ماكرون",
        "description_en": "Assorted sweet macarons — demo placeholder box.",
        "description_ar": "بوكس ماكرون متنوع — محتوى تجريبي.",
        "image": "24457758-sweets-6851675_1920.jpg",
        "prices": [
            {"label_ar": "بوكس", "label_en": "Box", "price": 4.5},
        ],
        "display_order": 2,
    },
    {
        "category_en": "Desserts",
        "name_en": "Dessert Pancake Stack",
        "name_ar": "بانكيك حلو",
        "description_en": "Sweet pancake stack for dessert lovers.",
        "description_ar": "طبق بانكيك حلو لعشاق الحلويات.",
        "image": "sklostudio-pancakes-5989136_1920.jpg",
        "prices": [
            {"label_ar": "طبق", "label_en": "Plate", "price": 3.5},
        ],
        "display_order": 3,
    },
    {
        "category_en": "Desserts",
        "name_en": "Coffee & Sweet Pair",
        "name_ar": "قهوة مع حلو",
        "description_en": "Coffee paired with a sweet treat — demo item.",
        "description_ar": "قهوة مع حلوى — عنصر تجريبي.",
        "image": "shixugang-coffee-563797.jpg",
        "prices": [
            {"label_ar": "زوج", "label_en": "Pair", "price": 3.0},
        ],
        "display_order": 4,
    },
]


def copy_image_to_uploads(source_name: str) -> str:
    """Copy an image from public/img into uploads/ with UUID filename."""
    src = IMG_DIR / source_name
    if not src.is_file():
        raise FileNotFoundError(f"Image not found: {src}")

    ext = src.suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError(f"Unsupported extension: {ext}")

    ensure_upload_dir()
    filename = f"{uuid.uuid4().hex}{ext}"
    relative_path = f"uploads/{filename}"
    dest = UPLOAD_DIR / filename
    shutil.copy2(src, dest)
    return relative_path


def main() -> None:
    if not IMG_DIR.is_dir():
        print(f"ERROR: image folder missing: {IMG_DIR}", file=sys.stderr)
        sys.exit(1)

    available = sorted(p.name for p in IMG_DIR.iterdir() if p.is_file())
    print("Available images in static/public/img/:")
    for name in available:
        print(f"  - {name}")
    print()

    db = SessionLocal()
    cat_created = cat_skipped = 0
    item_created = item_skipped = 0
    category_by_en: dict[str, Category] = {}

    try:
        for cat_data in CATEGORIES:
            existing = (
                db.query(Category)
                .filter(Category.name_en == cat_data["name_en"])
                .first()
            )
            if existing:
                print(f"SKIP category: {cat_data['name_en']} (already exists id={existing.id})")
                category_by_en[cat_data["name_en"]] = existing
                cat_skipped += 1
                continue

            category = Category(
                name_en=cat_data["name_en"],
                name_ar=cat_data["name_ar"],
                display_order=cat_data["display_order"],
                is_active=True,
            )
            db.add(category)
            db.flush()
            category_by_en[cat_data["name_en"]] = category
            print(f"CREATE category: {cat_data['name_en']} (id={category.id})")
            cat_created += 1

        for item_data in ITEMS:
            existing = (
                db.query(MenuItem)
                .filter(MenuItem.name_en == item_data["name_en"])
                .first()
            )
            if existing:
                print(f"SKIP item: {item_data['name_en']} (already exists id={existing.id})")
                item_skipped += 1
                continue

            category = category_by_en.get(item_data["category_en"])
            if not category:
                print(
                    f"ERROR: category missing for item {item_data['name_en']}: "
                    f"{item_data['category_en']}",
                    file=sys.stderr,
                )
                sys.exit(1)

            image_path = copy_image_to_uploads(item_data["image"])
            item = MenuItem(
                category_id=category.id,
                name_en=item_data["name_en"],
                name_ar=item_data["name_ar"],
                description_en=item_data["description_en"],
                description_ar=item_data["description_ar"],
                image_path=image_path,
                prices=item_data["prices"],
                display_order=item_data["display_order"],
                is_active=True,
            )
            db.add(item)
            db.flush()
            print(
                f"CREATE item: {item_data['name_en']} "
                f"(id={item.id}, image={image_path})"
            )
            item_created += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print()
    print("=== Seed summary ===")
    print(f"Categories created: {cat_created} | skipped: {cat_skipped}")
    print(f"Items created:      {item_created} | skipped: {item_skipped}")
    print()
    print(
        "NOTE: This is DEMO / PLACEHOLDER menu content for testing only. "
        "Review and replace via /admin/categories and /admin/items before client handoff."
    )


if __name__ == "__main__":
    main()
