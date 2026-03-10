import math
from config import NICHE_GENRES


def novelty_score(genre: str, installs: int, rating: float, ratings_count: int) -> float:
    genre_bonus = 1.4 if genre in NICHE_GENRES else 1.0

    installs_component = 1 / (1 + (installs / 200_000))

    raw_rating = max(0.3, min(1.0, rating / 5))
    confidence = math.log1p(ratings_count) / math.log1p(50_000)
    confidence = min(1.0, confidence)
    rating_component = raw_rating * confidence + 0.3 * (1 - confidence)

    return round(genre_bonus * installs_component * rating_component, 4)


def sort_apps(apps: list[dict], reverse: bool = True) -> list[dict]:
    for row in apps:
        row["Неочевидность"] = novelty_score(
            row["_genre"],
            row["_installs_int"],
            float(row["Рейтинг"]),
            row["Отзывы"],
        )
    return sorted(apps, key=lambda r: r["Неочевидность"], reverse=reverse)
