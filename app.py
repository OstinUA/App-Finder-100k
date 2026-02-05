import streamlit as st
from google_play_scraper import search, app as get_app_details
import pandas as pd
import random

st.set_page_config(page_title="App Finder", page_icon=None)

if 'seen_apps' not in st.session_state:
    st.session_state.seen_apps = set()

st.title("Google Play Random Finder")
st.write(f"Уникальных находок в этой сессии: {len(st.session_state.seen_apps)}")

min_installs_limit = st.sidebar.number_input("Минимум скачиваний", value=100000, step=50000)
results_limit = st.sidebar.number_input("Количество выводов", value=30, min_value=1, max_value=100)
search_limit = st.sidebar.slider("Глубина поиска", 50, 1000, 300)

if st.sidebar.button('Очистить историю'):
    st.session_state.seen_apps = set()
    st.rerun()

if st.button('Найти'):
    with st.spinner('Анализ Google Play...'):
        try:
            # Твой список категорий
            keywords = [
    "action", "adventure", "arcade", "board", "card", "casino", "casual", 
    "educational", "music", "puzzle", "racing", "role playing", "simulation", 
    "sports", "strategy", "trivia", "word", "horror", "zombie", "survival", 
    "shooter", "fps", "tps", "battle royale", "sniper", "tank", "robot", 
    "fighting", "wrestling", "boxing", "martial arts", "tower defense", 
    "idle", "clicker", "tycoon", "manager", "farm", "city builder", 
    "sandbox", "open world", "roguelike", "dungeon", "rpg", "mmorpg", 
    "moba", "gacha", "visual novel", "otome", "dating sim", "interactive story",
    "platformer", "runner", "parkour", "stealth", "hack and slash", 
    "match 3", "bubble shooter", "hidden object", "detective", "mystery", 
    "escape room", "logic", "brain training", "sudoku", "chess", "checkers", 
    "domino", "solitaire", "poker", "slots", "bingo", "blackjack", "mahjong",
    "football", "soccer", "basketball", "tennis", "golf", "cricket", 
    "baseball", "hockey", "volleyball", "skating", "snowboard", "skiing", 
    "fishing", "hunting", "billiards", "bowling", "darts", "archery",
    "car", "truck", "bus", "train", "plane", "flight simulator", "boat", 
    "motorcycle", "bike", "drift", "drag racing", "offroad", "parking",
    "tools", "productivity", "business", "finance", "money", "budget", 
    "stocks", "crypto", "bitcoin", "investing", "wallet", "banking", 
    "tax", "calculator", "converter", "scanner", "qr code", "barcode", 
    "pdf", "office", "notes", "calendar", "reminder", "alarm", "clock", 
    "flashlight", "compass", "level", "ruler", "speedometer", "gps", 
    "navigation", "maps", "weather", "news", "magazines", "comics", "manga",
    "social", "messenger", "chat", "video call", "dating", "meet", 
    "browser", "vpn", "proxy", "wifi", "internet", "security", "antivirus", 
    "cleaner", "booster", "battery", "file manager", "recovery", "backup",
    "camera", "photo editor", "video editor", "collage", "filters", 
    "beauty", "makeup", "fashion", "style", "design", "interior", 
    "drawing", "painting", "sketch", "coloring", "art", "music player", 
    "audio", "mp3", "radio", "podcast", "streaming", "recorder", 
    "voice changer", "equalizer", "ringtone", "wallpapers", "live wallpaper", 
    "launcher", "themes", "icons", "widgets", "keyboard", "emoji", "stickers",
    "health", "fitness", "workout", "gym", "yoga", "meditation", "sleep", 
    "diet", "calorie", "fasting", "water", "step counter", "running", 
    "cycling", "swimming", "medical", "anatomy", "pregnancy", "baby",
    "education", "learning", "language", "english", "spanish", "french", 
    "german", "japanese", "korean", "chinese", "dictionary", "translator", 
    "math", "physics", "chemistry", "biology", "history", "geography", 
    "coding", "programming", "python", "java", "linux", "developer",
    "shopping", "marketplace", "coupon", "discount", "delivery", "food", 
    "recipe", "cooking", "baking", "drink", "cocktail", "wine", 
    "travel", "hotel", "flight", "booking", "guide", "airline", 
    "taxi", "ride", "rental", "auto", "mechanic", "real estate",
    "horoscope", "astrology", "tarot", "psychic", "religion", "bible", 
    "quran", "prayer", "spirituality", "ghost", "ufo", 
    "prank", "joke", "meme", "funny", "entertainment", "tv", "movies",
    "lifestyle", "health & fitness", "food & drink", "travel & local", 
    "music & audio", "books & reference", "personalization", 
    "social networking", "photo & video", "maps & navigation", 
    "communication", "auto & vehicles", "art & design", "events", 
    "house & home", "video players", "family", "libraries & demo"
            ]
            
            query = random.choice(keywords)
            
            search_results = search(query, lang="ru", country="ru", n_hits=search_limit)
            random.shuffle(search_results)
            
            found_apps = []
            
            for item in search_results:
                app_id = item['appId']
                
                if app_id in st.session_state.seen_apps:
                    continue
                    
                try:
                    details = get_app_details(app_id)
                except:
                    continue

                raw_installs = details.get('installs')
                if raw_installs is None:
                    installs_count = 0
                else:
                    raw_installs = raw_installs.replace(',', '').replace('+', '').strip()
                    try:
                        installs_count = int(raw_installs)
                    except:
                        installs_count = 0
                
                score = details.get('score')
                if score is None:
                    score = 0.0
                
                if installs_count >= min_installs_limit:
                    clean_url = f"https://play.google.com/store/apps/details?id={app_id}"
                    
                    found_apps.append({
                        "appId": app_id,
                        "Название": details['title'],
                        "Скачивания": details.get('installs', '0'),
                        "Рейтинг": f"{score:.1f}",
                        "Жанр": details.get('genre', 'Unknown'),
                        "Ссылка": clean_url
                    })
                    st.session_state.seen_apps.add(app_id)
                
                if len(found_apps) >= results_limit:
                    break
            
            if found_apps:
                df = pd.DataFrame(found_apps)
                st.success(f"Категория поиска: {query}. Найдено: {len(found_apps)}")
                st.dataframe(df.drop(columns=['appId']), use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Скачать CSV", csv, "random_categories.csv", "text/csv")
            else:
                st.warning(f"По запросу '{query}' ничего нового не найдено. Попробуйте нажать кнопку еще раз.")
                
        except Exception as e:
            st.error(f"Ошибка: {e}")

st.divider()
st.caption("Данные Google Play (google-play-scraper)")
