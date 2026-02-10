# Google Play Random Finder 

A professional tool designed to streamline the process of finding and analyzing Android applications based on specific performance metrics.

### Core Functionality

* **Dynamic Filtering:** Filter apps by install thresholds (e.g., 100k+, 1M+) and store ratings.
* **Extensive Database:** Randomized queries across a comprehensive list of gaming and utility keywords.
* **Duplicate Prevention:** Uses `st.session_state` to ensure unique findings during a research session.
* **Data Export:** One-click CSV generation for further professional analysis.

### Technical Stack

* **Frontend:** Streamlit 
* **Data Processing:** Pandas 
* **API Wrapper:** Google-Play-Scraper 



### Technical Updates:

* **Logic Optimization:** Optimized the scraping loop to handle empty install data and rating exceptions gracefully.
* **Session Management:** Implemented a `set()` based tracking system for `appId` to maintain  lookup complexity for seen apps.
* **UI/UX:** Added sidebar controls for search parameters and a clear history function for session resets.
