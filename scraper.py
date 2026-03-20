import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
from google_play_scraper import app as get_app_details
from google_play_scraper import search

from config import (
    ALL_KEYWORDS,
    CACHE_TTL_DETAILS,
    CACHE_TTL_SEARCH,
    DEFAULT_WORKERS,
    SEARCH_LOCALES,
)
from db import get_cached_details, set_cached_details


@st.cache_data(show_spinner=False, ttl=CACHE_TTL_SEARCH)
def _fetch_search(query: str, lang: str, country: str, limit: int) -> list:
    """Fetch Google Play search results for a localized query.

    Args:
        query (str): The search phrase to submit to Google Play.
        lang (str): The language code used by the scraper request.
        country (str): The country code used to localize search results.
        limit (int): The maximum number of hits to request.

    Returns:
        list: A list of raw search result dictionaries. Returns an empty list
        when the scraper request fails.

    Examples:
        >>> isinstance(_fetch_search("puzzle", "en", "us", 10), list)
        True
    """
    try:
        return search(query, lang=lang, country=country, n_hits=limit)
    except Exception:
        return []


def _fetch_details(app_id: str) -> dict | None:
    """Fetch and cache detailed metadata for a Google Play application.

    Args:
        app_id (str): The Google Play application ID to retrieve.

    Returns:
        dict | None: The application details dictionary when retrieval succeeds,
        otherwise ``None`` if the scraper raises an exception.

    Examples:
        >>> result = _fetch_details("com.example.app")
        >>> result is None or isinstance(result, dict)
        True
    """
    cached = get_cached_details(app_id)
    if cached:
        return cached
    try:
        data = get_app_details(app_id)
        set_cached_details(app_id, data)
        return data
    except Exception:
        return None


def collect_candidates(
    queries_per_run: int,
    search_limit: int,
    seen_apps: set,
) -> list[str]:
    """Collect unique unseen application IDs from randomized search queries.

    Args:
        queries_per_run (int): The number of keywords to sample for the current
            run.
        search_limit (int): The number of search hits to request per keyword and
            locale combination.
        seen_apps (set): A set of application IDs that should be excluded from
            the candidate list.

    Returns:
        list[str]: A de-duplicated list of unseen Google Play application IDs
        discovered across the sampled queries and locales.

    Examples:
        >>> candidates = collect_candidates(2, 5, set())
        >>> isinstance(candidates, list)
        True
    """
    selected_queries = random.sample(ALL_KEYWORDS, k=min(queries_per_run, len(ALL_KEYWORDS)))
    selected_locales = random.sample(SEARCH_LOCALES, k=min(4, len(SEARCH_LOCALES)))

    candidate_ids: list[str] = []
    for query in selected_queries:
        for lang, country in selected_locales:
            results = _fetch_search(query, lang, country, search_limit)
            random.shuffle(results)
            candidate_ids.extend(
                item["appId"]
                for item in results
                if item.get("appId") and item["appId"] not in seen_apps
            )

    return list(dict.fromkeys(candidate_ids))


def fetch_details_batch(
    app_ids: list[str],
    min_installs: int,
    max_installs: int,
    results_limit: int,
) -> list[dict]:
    """Fetch, filter, and normalize metadata for a sampled batch of apps.

    Args:
        app_ids (list[str]): Candidate application IDs to inspect.
        min_installs (int): The minimum install count allowed in the output.
        max_installs (int): The maximum install count allowed in the output. A
            value of ``0`` disables the upper bound.
        results_limit (int): The target number of results shown to the user and
            the basis for the background sampling size.

    Returns:
        list[dict]: A list of normalized application rows ready for display in
        the UI.

    Examples:
        >>> isinstance(fetch_details_batch([], 0, 0, 10), list)
        True
    """
    sample_size = min(len(app_ids), results_limit * 8)
    sampled = random.sample(app_ids, sample_size) if sample_size else []

    found: list[dict] = []
    workers = min(DEFAULT_WORKERS, max(4, results_limit // 2 + 2))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_fetch_details, aid): aid for aid in sampled}
        for future in as_completed(futures):
            app_id = futures[future]
            details = future.result()
            if not details:
                continue

            installs_count = _parse_installs(details.get("installs"))
            if installs_count < min_installs:
                continue
            if max_installs and installs_count > max_installs:
                continue

            score = details.get("score") or 0.0
            genre = details.get("genre", "Unknown")

            found.append({
                "appId": app_id,
                "Название": details.get("title", app_id),
                "Скачивания": details.get("installs", "0"),
                "Рейтинг": f"{score:.1f}",
                "Жанр": genre,
                "Отзывы": details.get("ratings") or 0,
                "Обновлено": details.get("lastUpdatedOn", "—"),
                "Реклама": "Да" if details.get("containsAds") else "Нет",
                "Донат": "Да" if details.get("offersIAP") else "Нет",
                "Иконка": details.get("icon", ""),
                "Ссылка": f"https://play.google.com/store/apps/details?id={app_id}",
                "_installs_int": installs_count,
                "_score": score,
                "_genre": genre,
            })

    return found


def _parse_installs(val) -> int:
    """Convert a Google Play installs string into an integer count.

    Args:
        val (Any): A raw installs value such as ``"100,000+"`` or ``None``.

    Returns:
        int: The parsed install count, or ``0`` when the value is missing or
        cannot be interpreted as an integer.

    Examples:
        >>> _parse_installs("100,000+")
        100000
    """
    if not val:
        return 0
    try:
        return int(str(val).replace(",", "").replace("+", "").strip())
    except ValueError:
        return 0
