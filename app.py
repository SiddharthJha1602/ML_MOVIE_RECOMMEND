"""CineMatch - Streamlit entry point.  Run with:  python -m streamlit run app.py"""
from __future__ import annotations

import streamlit as st

from src import config
from src.data_loader import dataset_paths, load_dataset, setup_instructions
from src.recommender import RecommendationEngine
from src.utils import CineMatchError, DatasetError
from ui import pages
from ui.styles import inject_css

st.set_page_config(page_title="CineMatch | Movie Recommender", page_icon="🎬", layout="wide")
inject_css()


@st.cache_resource(show_spinner="Loading dataset and training models...")
def build_engine(data_dir: str, signature: tuple) -> RecommendationEngine:
    """Load the data and build every model once. ``signature`` (file sizes/mtimes) busts the cache
    when the CSV files change."""
    return RecommendationEngine(load_dataset(data_dir))


def _signature(data_dir) -> tuple:
    sig = []
    for path in dataset_paths(data_dir):
        stat = path.stat() if path.is_file() else None
        sig.append((str(path), stat.st_size if stat else None, stat.st_mtime_ns if stat else None))
    return tuple(sig)


def main() -> None:
    data_dir = config.get_data_dir()
    try:
        engine = build_engine(str(data_dir), _signature(data_dir))
    except DatasetError as exc:
        st.title("🎬 CineMatch")
        st.error(f"**Dataset problem:** {exc}")
        st.info(setup_instructions(data_dir))
        st.caption("After the files are in place, refresh this page.")
        st.stop()
    except CineMatchError as exc:
        st.title("🎬 CineMatch")
        st.error(f"The models could not be built: {exc}")
        st.stop()

    with st.sidebar:
        st.markdown("## 🎬 CineMatch")
        page = st.radio("Navigate", pages.PAGES, label_visibility="collapsed")
        st.divider()
        st.caption("Data: MovieLens Small (GroupLens). Built with Python, pandas, scikit-learn and Streamlit.")

    renderers = {
        "Home": pages.render_home,
        "Recommendations": pages.render_recommendations,
        "Explore Movies": pages.render_explore,
        "Model Insights": pages.render_insights,
        "About the Models": pages.render_about,
    }
    renderers[page](engine)


main()
