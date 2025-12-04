import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from cachebox import TTLCache, cached

logger = logging.getLogger("epicnotify")

BASE_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=ru&country=RU&allowCountries=FR"
TZ = timezone(timedelta(hours=3))


@dataclass
class Game:
    id: str
    title: str
    description: str | None
    url: str
    price_original: float
    fmt_price_original: str
    price_discount: float
    fmt_price_discount: str
    currency: str
    start_date: datetime
    end_date: datetime
    image_url: str | None
    is_mystery: bool = False

    @property
    def is_active(self) -> bool:
        return self.start_date <= datetime.now(TZ) <= self.end_date


def _parse_game_element(element: dict[str, Any]) -> Game | None:
    try:
        promotions: dict[str, Any] | None = element.get("promotions")
        if not promotions:
            return None

        active_offers: list[dict[str, Any]] = promotions.get("promotionalOffers", [])
        upcoming_offers: list[dict[str, Any]] = promotions.get(
            "upcomingPromotionalOffers", []
        )

        free_offer: dict[str, Any] | None = None
        for promotion in active_offers + upcoming_offers:
            offers_list: list[dict[str, Any]] = promotion.get("promotionalOffers", [])
            for offer in offers_list:
                if offer.get("discountSetting", {}).get("discountPercentage") != 0:
                    continue

                free_offer = offer
                break

        if not free_offer:
            return None

        mappings: list[dict[str, Any]] = element.get("catalogNs", {}).get(
            "mappings", []
        )
        page: dict[str, Any] | None = next(
            (i for i in mappings if i["pageType"] == "productHome"), None
        )
        page_slug: str | None = page["pageSlug"] if page else None
        game_url = "https://store.epicgames.com/ru/"
        if page_slug:
            game_url += f"p/{page_slug}"

        price_data = element.get("price", {}).get("totalPrice", {})
        decimals = 10 ** price_data.get("currencyInfo", {}).get("decimals", 2)
        price_orig = price_data.get("originalPrice", 0) / decimals
        price_disc = price_data.get("discountPrice", 0) / decimals
        currency = price_data.get("currencyCode", "RUB")

        fmt_price_original = price_data.get("fmtPrice", {}).get("originalPrice")
        if not fmt_price_original:
            fmt_price_original = f"{price_orig} {currency}"
        fmt_price_discount = price_data.get("fmtPrice", {}).get("discountPrice")
        if not fmt_price_discount:
            fmt_price_discount = f"{price_disc} {currency}"
        if fmt_price_discount == "0":
            fmt_price_discount = "Бесплатно"

        start_date_str = free_offer["startDate"][:19] + "+00:00"
        end_date_str = free_offer["endDate"][:19] + "+00:00"
        start_date = datetime.fromisoformat(start_date_str).astimezone(TZ)
        end_date = datetime.fromisoformat(end_date_str).astimezone(TZ)

        key_images = element.get("keyImages", [])
        target_img: str | None = next(
            (
                i["url"]
                for i in key_images
                if i["type"] in ("OfferImageWide", "VaultClosed")
            ),
            None,
        )

        is_mystery = any(i["type"] == "VaultClosed" for i in key_images)

        return Game(
            id=element["id"],
            title=element["title"],
            description=element.get("description"),
            url=game_url,
            price_original=price_orig,
            fmt_price_original=fmt_price_original,
            price_discount=price_disc,
            fmt_price_discount=fmt_price_discount,
            currency=currency,
            start_date=start_date,
            end_date=end_date,
            image_url=target_img,
            is_mystery=is_mystery,
        )

    except Exception:
        logger.exception("Failed to parse game element")
        return None


@cached(TTLCache(maxsize=1, ttl=300))
def get_free_games() -> tuple[list[Game], list[Game]]:
    try:
        resp = requests.get(BASE_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        elements = (
            data.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )

        active: list[Game] = []
        upcoming: list[Game] = []

        for element in elements:
            game = _parse_game_element(element)
            if not game:
                continue
            if game.is_active:
                active.append(game)
            else:
                upcoming.append(game)

        return active, upcoming

    except Exception:
        logger.exception("Failed to fetch games from Epic Games")
        return [], []
