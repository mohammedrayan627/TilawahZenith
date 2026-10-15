import streamlit as st
import requests

# TilawahZenith — Quran reader, translation, and recitation
# Run with: streamlit run app.py

API_BASE = "https://api.alquran.cloud/v1"
AUDIO_BASE = "https://cdn.islamic.network/quran/audio-surah/128"

st.set_page_config(
    page_title="TilawahZenith | Holy Quran",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #071b17 0%, #0b211b 38%, #101b18 100%);
        color: #f7f4e9;
    }
    [data-testid="stSidebar"] {
        background: #061510;
        border-right: 1px solid #254b3b;
    }
    h1, h2, h3 { color: #f1d58a !important; }
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: #f3f0e6;
    }
    .hero {
        padding: 1.5rem 1.7rem;
        border: 1px solid #426d51;
        border-radius: 20px;
        background: linear-gradient(135deg, #123d2c, #0b241d 70%);
        margin-bottom: 1rem;
    }
    .hero-kicker {
        color: #e9cc7b;
        letter-spacing: .12em;
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .hero-title {
        color: #fff5d8;
        font-size: 2.1rem;
        font-weight: 800;
        margin: .35rem 0;
    }
    .hero-subtitle { color: #d6e4d7; font-size: 1rem; }
    .ayah-card {
        background: rgba(255,255,255,.045);
        border: 1px solid rgba(214, 190, 113, .27);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin: .7rem 0;
    }
    .ayah-meta { color: #e9cc7b; font-size: .82rem; margin-bottom: .7rem; }
    .arabic {
        font-family: "Noto Naskh Arabic", "Amiri", serif;
        color: #fff7df;
        font-size: 2rem;
        line-height: 2.1;
        text-align: right;
        direction: rtl;
        margin: .4rem 0 1rem;
    }
    .translation {
        color: #e4eadf;
        font-size: 1rem;
        line-height: 1.8;
        text-align: left;
    }
    .small-note { color: #c5d4c7; font-size: .85rem; }
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #bfa45a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data helpers ----------
@st.cache_data(ttl=3600)
def fetch_surahs():
    response = requests.get(f"{API_BASE}/surah", timeout=25)
    response.raise_for_status()
    return response.json()["data"]


@st.cache_data(ttl=3600)
def fetch_surah_text(number, translation_edition):
    editions = f"quran-uthmani,{translation_edition}"
    response = requests.get(
        f"{API_BASE}/surah/{number}/editions/{editions}",
        timeout=40,
    )
    response.raise_for_status()
    result = response.json()["data"]
    return result[0]["ayahs"], result[1]["ayahs"]


# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Read • Listen • Reflect</div>
      <div class="hero-title">📖 TilawahZenith</div>
      <div class="hero-subtitle">
        A peaceful place to read the Holy Quran, explore translations,
        and listen to recitation.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🕌 Navigation")
    page = st.radio(
        "Choose a section",
        ["Quran Reader", "Bookmarks", "About"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("### 🎧 Reciter")
    reciters = {
        "Mishary Rashid Alafasy": "ar.alafasy",
        "Abdur Rahman as-Sudais": "ar.abdurrahmaansudais",
        "Maher Al-Muaiqly": "ar.mahermuaiqly",
        "Mahmoud Khalil Al-Husary": "ar.husary",
    }
    selected_reciter_name = st.selectbox("Choose reciter", list(reciters))
    reciter_id = reciters[selected_reciter_name]
    st.markdown(
        '<div class="small-note">Audio and Quran data need an internet connection.</div>',
        unsafe_allow_html=True,
    )

if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "selected_surah" not in st.session_state:
    st.session_state.selected_surah = 1

# ---------- Bookmarks page ----------
if page == "Bookmarks":
    st.header("🔖 Your Bookmarks")
    if not st.session_state.bookmarks:
        st.info("You have no bookmarks yet. Open the Quran Reader and save an ayah.")
    else:
        for item in st.session_state.bookmarks:
            left, right = st.columns([5, 1])
            with left:
                st.markdown(
                    f"**{item['surah_name']} — Ayah {item['ayah']}**  \n"
                    f"{item['arabic']}"
                )
                st.caption(item["translation"])
            with right:
                if st.button("Remove", key=f"remove_{item['surah']}_{item['ayah']}"):
                    st.session_state.bookmarks = [
                        b for b in st.session_state.bookmarks
                        if not (b["surah"] == item["surah"] and b["ayah"] == item["ayah"])
                    ]
                    st.rerun()

# ---------- About page ----------
elif page == "About":
    st.header("About TilawahZenith")
    st.write(
        "TilawahZenith is a Quran reading companion with Arabic text, "
        "translations, recitation audio, surah search, and session bookmarks."
    )
    st.info(
        "Quran text, translations, and audio are provided by external online services. "
        "Please verify translations with trusted scholars and published Quran editions."
    )
    st.markdown("**Features**")
    st.markdown(
        "- Browse all 114 surahs\n"
        "- Read Arabic Quran text with ayah numbers\n"
        "- Read an available translation\n"
        "- Listen to a full-surah recitation\n"
        "- Search for a surah or filter ayahs by text\n"
        "- Save bookmarks during your current session"
    )

# ---------- Quran reader page ----------
else:
    try:
        surahs = fetch_surahs()

        search_surah = st.text_input(
            "🔎 Find a surah by name or number",
            placeholder="Try Al-Fatihah, Ya-Sin, or 36",
        ).strip().lower()

        matching_surahs = [
            surah for surah in surahs
            if search_surah in surah["name"].lower()
            or search_surah in surah["englishName"].lower()
            or search_surah in surah["englishNameTranslation"].lower()
            or search_surah == str(surah["number"])
        ]

        if not matching_surahs:
            st.warning("No surah found. Try another name or number.")
            st.stop()

        # Keep the selected surah in session state, while respecting search filtering.
        options = matching_surahs
        default_index = next(
            (i for i, s in enumerate(options)
             if s["number"] == st.session_state.selected_surah),
            0,
        )
        selected_surah = st.selectbox(
            "Select a Surah",
            options,
            index=default_index,
            format_func=lambda s: (
                f'{s["number"]:03d}  •  {s["englishName"]} '
                f'— {s["name"]}'
            ),
        )
        st.session_state.selected_surah = selected_surah["number"]

        st.markdown(f"## {selected_surah['name']}")
        st.markdown(f"### {selected_surah['englishName']}")
        st.caption(
            f'{selected_surah["englishNameTranslation"]}  ·  '
            f'{selected_surah["numberOfAyahs"]} ayahs  ·  '
            f'{selected_surah["revelationType"]}'
        )

        translation_options = {
            "English — Saheeh International": "en.sahih",
            "Urdu — Jalandhry": "ur.jalandhry",
            "Bengali": "bn.bengali",
            "French": "fr.hamidullah",
            "Indonesian": "id.indonesian",
        }
        chosen_translation = st.selectbox(
            "Translation language",
            list(translation_options),
        )
        translation_edition = translation_options[chosen_translation]

        audio_url = (
            f"{AUDIO_BASE}/{reciter_id}/{selected_surah['number']}.mp3"
        )
        st.markdown("### 🎧 Listen to the complete surah")
        st.caption(f"Reciter: {selected_reciter_name}")
        st.audio(audio_url, format="audio/mp3")

        with st.spinner("Loading Quran text and translation..."):
            arabic_ayahs, translated_ayahs = fetch_surah_text(
                selected_surah["number"], translation_edition
            )

        filter_text = st.text_input(
            "Search within this surah (Arabic or translation)",
            placeholder="Enter a word to filter ayahs",
        ).strip().lower()

        st.markdown("### 📜 Ayahs")
        shown_count = 0
        for arabic, translated in zip(arabic_ayahs, translated_ayahs):
            arabic_text = arabic["text"]
            translated_text = translated["text"]
            ayah_number = arabic["numberInSurah"]

            if filter_text and (
                filter_text not in arabic_text.lower()
                and filter_text not in translated_text.lower()
            ):
                continue

            shown_count += 1
            st.markdown(
                f"""
                <div class="ayah-card">
                  <div class="ayah-meta">
                    {selected_surah["englishName"]} · Ayah {ayah_number}
                  </div>
                  <div class="arabic" lang="ar" dir="rtl">{arabic_text}</div>
                  <div class="translation">{translated_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            bookmark_key = f"bookmark_{selected_surah['number']}_{ayah_number}"
            already_saved = any(
                b["surah"] == selected_surah["number"] and b["ayah"] == ayah_number
                for b in st.session_state.bookmarks
            )
            if already_saved:
                st.caption("🔖 Saved to bookmarks")
            elif st.button("🔖 Bookmark this ayah", key=bookmark_key):
                st.session_state.bookmarks.append(
                    {
                        "surah": selected_surah["number"],
                        "surah_name": selected_surah["englishName"],
                        "ayah": ayah_number,
                        "arabic": arabic_text,
                        "translation": translated_text,
                    }
                )
                st.success("Ayah bookmarked for this session.")
                st.rerun()

        if shown_count == 0:
            st.info("No ayahs match that search. Try another word.")

        st.divider()
        previous_col, info_col, next_col = st.columns([1, 2, 1])
        with previous_col:
            if selected_surah["number"] > 1:
                if st.button("← Previous surah"):
                    st.session_state.selected_surah = selected_surah["number"] - 1
                    st.rerun()
        with info_col:
            st.caption("Bookmarks are kept in this browser session and may reset.")
        with next_col:
            if selected_surah["number"] < 114:
                if st.button("Next surah →"):
                    st.session_state.selected_surah = selected_surah["number"] + 1
                    st.rerun()

    except requests.RequestException:
        st.error(
            "Couldn't load Quran data right now. Check your internet connection "
            "and try again later."
        )
    except (KeyError, IndexError, ValueError, TypeError):
        st.error(
            "The Quran service returned unexpected data. Please refresh and try again."
        )

st.divider()
st.caption(
    "TilawahZenith • Handle Quran text respectfully. "
    "Audio and translation availability depends on the external service."
)
