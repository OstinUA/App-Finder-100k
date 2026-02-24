import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st
from google_play_scraper import app as get_app_details
from google_play_scraper import search

st.set_page_config(page_title="App Finder", page_icon=None)

if "seen_apps" not in st.session_state:
    st.session_state.seen_apps = set()

@st.cache_data(show_spinner=False, ttl=60 * 60 * 6)
def fetch_search_results(query: str, limit: int):
    return search(query, lang="ru", country="ru", n_hits=limit)


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_app_details_cached(app_id: str):
    return get_app_details(app_id)


def safe_parse_installs(installs_value) -> int:
    if not installs_value:
        return 0
    normalized = str(installs_value).replace(",", "").replace("+", "").strip()
    try:
        return int(normalized)
    except ValueError:
        return 0


def novelty_score(genre: str, installs: int, rating: float) -> float:
    niche_genres = {
        "Word",
        "Trivia",
        "Music",
        "Board",
        "Card",
        "Educational",
        "Adventure",
        "Simulation",
        "Strategy",
        "Role Playing",
    }
    genre_bonus = 1.4 if genre in niche_genres else 1.0

    # Чем меньше установок и при этом выше рейтинг — тем более неочевидная находка.
    installs_component = 1 / (1 + (installs / 200_000))
    rating_component = max(0.3, min(1.0, rating / 5))
    return genre_bonus * installs_component * rating_component


st.title("Google Play Random Finder")
st.write(f"Уникальных находок в этой сессии: {len(st.session_state.seen_apps)}")

min_installs_limit = st.sidebar.number_input("Минимум скачиваний", value=100000, step=50000)
max_installs_limit = st.sidebar.number_input("Максимум скачиваний (для неочевидных)", value=5000000, step=100000)
results_limit = st.sidebar.number_input("Количество выводов", value=30, min_value=1, max_value=100)
search_limit = st.sidebar.slider("Глубина поиска на запрос", 30, 400, 140)
queries_per_run = st.sidebar.slider("Количество запросов за запуск", 2, 10, 4)
prefer_non_obvious = st.sidebar.checkbox("Показывать более неочевидные игры", value=True)

if st.sidebar.button("Очистить историю"):
    st.session_state.seen_apps = set()
    st.rerun()

if st.button("Найти"):
    with st.spinner("Анализ Google Play..."):
        try:
            game_keywords = [
                "action",
                "adventure",
                "arcade",
                "puzzle",
                "racing",
                "role playing",
                "simulation",
                "sports",
                "strategy",
                "trivia",
                "word",
                "horror",
                "survival",
                "shooter",
                "tower defense",
                "roguelike",
                "dungeon",
                "visual novel",
                "platformer",
                "escape room",
                "chess",
                "mahjong",
            ]
            niche_keywords = [
                "turn based tactics",
                "soulslike",
                "deckbuilder",
                "tactical rpg",
                "incremental game",
                "metroidvania",
                "immersive sim",
                "survival horror indie",
                "point and click adventure",
                "narrative puzzle",
                "asymmetric multiplayer",
                "hidden gems",
                "minimalist puzzle",
                "retro pixel rpg",
                "party game local",
            ]
            keyword_pool = niche_keywords * 3 + game_keywords

            selected_queries = random.sample(keyword_pool, k=min(queries_per_run, len(keyword_pool)))

            candidate_ids = []
            for query in selected_queries:
                search_results = fetch_search_results(query, search_limit)
                random.shuffle(search_results)
                candidate_ids.extend(
                    item["appId"]
                    for item in search_results
                    if item.get("appId") and item["appId"] not in st.session_state.seen_apps
                )

            unique_candidate_ids = list(dict.fromkeys(candidate_ids))
            # Избыточная выборка, чтобы после фильтрации гарантированно набрать results_limit.
            sample_size = min(len(unique_candidate_ids), results_limit * 6)
            sampled_ids = random.sample(unique_candidate_ids, sample_size) if sample_size else []

            found_apps = []
            workers = min(16, max(4, results_limit // 2 + 2))
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_id = {executor.submit(fetch_app_details_cached, app_id): app_id for app_id in sampled_ids}

                for future in as_completed(future_to_id):
                    app_id = future_to_id[future]
                    try:
                        details = future.result()
                    except Exception:
                        continue

                    installs_count = safe_parse_installs(details.get("installs"))
                    score = details.get("score") or 0.0
                    genre = details.get("genre", "Unknown")

                    if installs_count < min_installs_limit:
                        continue
                    if prefer_non_obvious and installs_count > max_installs_limit:
                        continue

                    clean_url = f"https://play.google.com/store/apps/details?id={app_id}"
                    found_apps.append(
                        {
                            "appId": app_id,
                            "Название": details.get("title", app_id),
                            "Скачивания": details.get("installs", "0"),
                            "Рейтинг": f"{score:.1f}",
                            "Жанр": genre,
                            "Неочевидность": round(novelty_score(genre, installs_count, score), 3),
                            "Ссылка": clean_url,
                        }
                    )
                    st.session_state.seen_apps.add(app_id)

            if found_apps:
                found_apps.sort(key=lambda row: row["Неочевидность"], reverse=True)
                top_found_apps = found_apps[:results_limit]

                df = pd.DataFrame(top_found_apps)
                st.success(
                    f"Запросы: {', '.join(selected_queries)}. Найдено: {len(top_found_apps)}"
                )
                st.dataframe(df.drop(columns=["appId"]), use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Скачать CSV", csv, "random_categories.csv", "text/csv")
            else:
                st.warning(
                    "Ничего нового не найдено после фильтрации. "
                    "Снизьте минимум скачиваний или отключите фильтр неочевидности."
                )

        except Exception as e:
            st.error(f"Ошибка: {e}")

st.divider()
st.caption("Данные Google Play (google-play-scraper)")
