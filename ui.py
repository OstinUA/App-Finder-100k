import pandas as pd
import streamlit as st

from config import (
    DEFAULT_MAX_INSTALLS,
    DEFAULT_MIN_INSTALLS,
    DEFAULT_QUERIES_PER_RUN,
    DEFAULT_RESULTS_LIMIT,
    DEFAULT_SEARCH_DEPTH,
)
from db import clear_seen_apps, seen_apps_count


def render_sidebar() -> dict:
    st.sidebar.header("Параметры поиска")

    min_installs = st.sidebar.number_input(
        "Минимум скачиваний", value=DEFAULT_MIN_INSTALLS, step=10_000
    )
    max_installs = st.sidebar.number_input(
        "Максимум скачиваний (0 = без ограничения)",
        value=DEFAULT_MAX_INSTALLS,
        step=100_000,
    )
    results_limit = st.sidebar.number_input(
        "Количество результатов", value=DEFAULT_RESULTS_LIMIT, min_value=1, max_value=200
    )
    search_limit = st.sidebar.slider("Глубина поиска на запрос", 30, 400, DEFAULT_SEARCH_DEPTH)
    queries_per_run = st.sidebar.slider("Запросов за запуск", 2, 20, DEFAULT_QUERIES_PER_RUN)
    sort_by_novelty = st.sidebar.checkbox("Сортировать по неочевидности", value=True)

    st.sidebar.divider()
    total_seen = seen_apps_count()
    st.sidebar.caption(f"В базе уникальных приложений: **{total_seen}**")
    if st.sidebar.button("Очистить историю"):
        clear_seen_apps()
        st.rerun()

    return {
        "min_installs": int(min_installs),
        "max_installs": int(max_installs),
        "results_limit": int(results_limit),
        "search_limit": int(search_limit),
        "queries_per_run": int(queries_per_run),
        "sort_by_novelty": sort_by_novelty,
    }


def render_results(found_apps: list[dict], selected_queries: list[str], results_limit: int):
    if not found_apps:
        st.warning(
            "Ничего не найдено. Снизьте минимум скачиваний или уберите ограничение максимума."
        )
        return

    top = found_apps[:results_limit]
    st.success(f"Запросы: {', '.join(selected_queries)} | Найдено: {len(top)}")

    display_cols = ["Название", "Скачивания", "Рейтинг", "Жанр",
                    "Отзывы", "Реклама", "Донат", "Обновлено", "Неочевидность", "Ссылка"]

    df = pd.DataFrame(top)
    existing = [c for c in display_cols if c in df.columns]
    st.dataframe(df[existing], use_container_width=True)

    export_cols = [c for c in df.columns if not c.startswith("_") and c != "Иконка"]
    csv = df[export_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Скачать CSV", csv, "results.csv", "text/csv")
