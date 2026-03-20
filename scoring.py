import math
from config import NICHE_GENRES


def novelty_score(genre: str, installs: int, rating: float, ratings_count: int) -> float:
    """Calculate a novelty score for an application discovery result.

    The score favors niche genres, lower install counts, and stronger ratings
    while discounting ratings with little review volume.

    Args:
        genre (str): The application genre label returned by Google Play.
        installs (int): The parsed install count for the application.
        rating (float): The average star rating on a five-point scale.
        ratings_count (int): The number of ratings used to estimate confidence
            in the average score.

    Returns:
        float: A rounded novelty score where larger values indicate more
        unusual and promising results.

    Examples:
        >>> novelty_score("Puzzle", 10000, 4.7, 1200) > 0
        True
    """
    genre_bonus = 1.4 if genre in NICHE_GENRES else 1.0

    installs_component = 1 / (1 + (installs / 200_000))

    raw_rating = max(0.3, min(1.0, rating / 5))
    confidence = math.log1p(ratings_count) / math.log1p(50_000)
    confidence = min(1.0, confidence)
    rating_component = raw_rating * confidence + 0.3 * (1 - confidence)

    return round(genre_bonus * installs_component * rating_component, 4)


def sort_apps(apps: list[dict], reverse: bool = True) -> list[dict]:
    """Annotate and sort application rows by novelty score.

    Args:
        apps (list[dict]): Application result rows containing the private
            metadata fields required for novelty calculation.
        reverse (bool, optional): Whether to sort from highest novelty score to
            lowest. Defaults to ``True``.

    Returns:
        list[dict]: A new list of application rows ordered by their computed
        ``"Неочевидность"`` value.

    Raises:
        KeyError: Raised if an application row is missing a required metadata
            field such as ``"_genre"`` or ``"_installs_int"``.
        ValueError: Raised if ``row["Рейтинг"]`` cannot be converted to
            ``float``.

    Examples:
        >>> rows = [{"_genre": "Puzzle", "_installs_int": 1000, "Рейтинг": "4.8", "Отзывы": 12}]
        >>> sort_apps(rows)[0]["Неочевидность"] > 0
        True
    """
    for row in apps:
        row["Неочевидность"] = novelty_score(
            row["_genre"],
            row["_installs_int"],
            float(row["Рейтинг"]),
            row["Отзывы"],
        )
    return sorted(apps, key=lambda r: r["Неочевидность"], reverse=reverse)
