"""
One-off migration: convert MenuItem.prices from flat dict to bilingual tier list.

Usage:
    python scripts/migrate_prices_bilingual.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.core.database import SessionLocal
from app.core.menu_prices import is_tier_list, migrate_legacy_prices
from app.models.menu_item import MenuItem


def main() -> None:
    db = SessionLocal()
    unknown_all: list[str] = []
    try:
        items = db.query(MenuItem).order_by(MenuItem.id).all()
        for item in items:
            before = item.prices
            print(f"\nItem {item.id} ({item.name_en}) BEFORE: {before!r}")

            if is_tier_list(before):
                print("  -> already migrated, skipping")
                continue

            if not isinstance(before, dict):
                print(f"  -> unexpected format, skipping")
                continue

            tiers, unknown = migrate_legacy_prices(before)
            unknown_all.extend(unknown)
            item.prices = tiers
            print(f"  AFTER: {tiers!r}")
            if unknown:
                print(f"  -> unknown tier keys (label_ar left empty): {unknown}")

        db.commit()
        print("\nMigration complete.")
        if unknown_all:
            print(f"Flagged unknown keys for manual Arabic labels: {sorted(set(unknown_all))}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
