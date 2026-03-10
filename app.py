import streamlit as st

from db import init_db, load_seen_apps, save_seen_apps
from scraper import collect_candidates, fetch_details_batch
from scoring import sort_apps
from ui import render_results, render_sidebar

st.set_page_config(page_title="GP Random Finder", page_icon=None)
init_db()

st.title("Google Play Random Finder")

params = render_sidebar()

if st.button("Найти", type="primary"):
    with st.spinner("Анализ Google Play..."):
        seen = load_seen_apps()

        candidates = collect_candidates(
            queries_per_run=params["queries_per_run"],
            search_limit=params["search_limit"],
            seen_apps=seen,
        )

        found = fetch_details_batch(
            app_ids=candidates,
            min_installs=params["min_installs"],
            max_installs=params["max_installs"],
            results_limit=params["results_limit"],
        )

        if params["sort_by_novelty"]:
            found = sort_apps(found)

        new_ids = {row["appId"] for row in found}
        save_seen_apps(new_ids)

        selected_queries_info = candidates[:params["queries_per_run"]]
        render_results(found, selected_queries_info, params["results_limit"])

st.divider()
st.caption("Данные Google Play (google-play-scraper)")
