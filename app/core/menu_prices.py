from decimal import Decimal, InvalidOperation

KNOWN_LABEL_AR: dict[str, str] = {
    "small": "صغير",
    "large": "كبير",
    "regular": "عادي",
    "medium": "وسط",
}

KNOWN_LABEL_EN: dict[str, str] = {
    "small": "Small",
    "large": "Large",
    "regular": "Regular",
    "medium": "Medium",
}


def is_tier_list(prices) -> bool:
    return isinstance(prices, list) and (
        not prices or isinstance(prices[0], dict) and "label_ar" in prices[0]
    )


def migrate_legacy_prices(prices: dict) -> tuple[list[dict], list[str]]:
    """Convert old flat dict to bilingual tier list. Returns (tiers, unknown_keys)."""
    tiers: list[dict] = []
    unknown: list[str] = []
    for key, price in prices.items():
        key_lower = str(key).strip().lower()
        label_ar = KNOWN_LABEL_AR.get(key_lower, "")
        label_en = KNOWN_LABEL_EN.get(key_lower, str(key).strip())
        if not label_ar:
            unknown.append(str(key))
        tiers.append(
            {
                "label_ar": label_ar,
                "label_en": label_en,
                "price": float(price),
            }
        )
    return tiers, unknown


def parse_price_tiers(
    label_ar: list[str],
    label_en: list[str],
    price_values: list[str],
) -> tuple[list[dict], str | None]:
    tiers: list[dict] = []
    row_count = max(len(label_ar), len(label_en), len(price_values))

    for i in range(row_count):
        ar = label_ar[i].strip() if i < len(label_ar) else ""
        en = label_en[i].strip() if i < len(label_en) else ""
        val = price_values[i].strip() if i < len(price_values) else ""

        if not ar and not en and not val:
            continue

        if not ar:
            return [], "Every price tier must have an Arabic label."
        if not en:
            return [], "Every price tier must have an English label."
        if not val:
            return [], "Every price tier must have a price."

        try:
            price = float(Decimal(val))
        except (InvalidOperation, ValueError):
            return [], f"Invalid price value: {val!r}"

        tiers.append({"label_ar": ar, "label_en": en, "price": price})

    if not tiers:
        return [], "At least one price tier is required."

    return tiers, None


def format_prices(prices) -> str:
    if not prices:
        return "—"
    if isinstance(prices, dict):
        return ", ".join(f"{k}: {v:g}" for k, v in prices.items())
    parts: list[str] = []
    for tier in prices:
        if not isinstance(tier, dict):
            continue
        label_ar = tier.get("label_ar", "")
        label_en = tier.get("label_en", "")
        price = tier.get("price", "")
        if label_ar and label_en:
            parts.append(f"{label_ar}/{label_en}: {price:g}")
        elif label_en:
            parts.append(f"{label_en}: {price:g}")
        else:
            parts.append(f"{label_ar}: {price:g}")
    return ", ".join(parts) if parts else "—"
