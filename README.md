# 🎬 CineMatch - Movie Recommendation System

A Streamlit web app that recommends movies from the **MovieLens Small** dataset using four classic
approaches: popularity, content-based (genres), collaborative filtering (user rating patterns) and a hybrid.
It was converted from a Jupyter notebook into a normal Python project that runs on Windows in VS Code.
The Jupyter notebook is **optional** - the app runs without it.

## Quick start (Windows, VS Code terminal / PowerShell)

Open the `CineMatch` folder in VS Code (`File > Open Folder`), open a terminal (`Ctrl+``), then:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/download_dataset.py
python -m streamlit run app.py
```

The app opens at **http://localhost:8501**. Press `Ctrl+C` in the terminal to stop it.

> The dataset is **not** included. `scripts/download_dataset.py` downloads the official MovieLens Small zip
> (needs internet once). If you already have the zip (e.g. the notebook's `movie dataset.zip`), use
> `python scripts/download_dataset.py --zip "C:\path\to\movie dataset.zip"`. See `data/README.md`.
> If the files are missing the app shows instructions instead of crashing.

### Troubleshooting

| Problem | Fix |
|---|---|
| `.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, activate again. Or use Command Prompt: `.venv\Scripts\activate.bat`. |
| `py` / `python` is not recognized | Install Python 3.10+ from python.org and tick **"Add python.exe to PATH"**, then reopen the terminal. Try `python -m venv .venv` if `py` is missing. |
| `pip install` fails | Update pip (`python -m pip install --upgrade pip`), check your internet/proxy, and make sure the venv is active (the prompt starts with `(.venv)`). Use a 64-bit Python 3.10-3.13. |
| App says the dataset is missing | Run `python scripts/download_dataset.py` (or `--zip ...`), then refresh the browser page. |
| `streamlit` is not recognized | Always start it with `python -m streamlit run app.py`. |
| Port 8501 already in use | `python -m streamlit run app.py --server.port 8502` |
| `download_dataset.py` cannot download | Download `ml-latest-small.zip` manually from https://grouplens.org/datasets/movielens/latest/ and use the `--zip` option. |

## Pages

1. **Home** - branding, dataset statistics, quick recommender and top-rated picks.
2. **Recommendations** - choose a movie, a method and how many results; score explanations.
3. **Explore Movies** - title search, genre filters (any/all), sorting by popularity, rating, rating count, title or year, and pagination.
4. **Model Insights** - totals, rating distribution, genre distribution, most-rated and highest-rated movies (with a minimum-ratings slider), and an on-demand offline evaluation. All numbers are computed from the loaded dataset.
5. **About the Models** - plain-language comparison table and the formulas.

## The four models

| Model | File | Idea |
|---|---|---|
| Popularity | `src/popularity_model.py` | `weighted = v/(v+m)·R + m/(v+m)·C` (R = movie mean rating, v = its rating count, C = global mean, m = 75th percentile of rating counts) |
| Content-based | `src/content_model.py` | Genre strings → TF-IDF vectors → cosine similarity to the selected movie. **Genres only** - no plots, actors or directors exist in the data. |
| Collaborative | `src/collaborative_model.py` | Sparse movie × user rating matrix → scikit-learn `NearestNeighbors` (cosine, brute force) → movies with similar rating patterns |
| Hybrid | `src/hybrid_model.py` | `hybrid_score = 0.75 · similarity + 0.25 · popularity_normalized`, applied to the 50 most genre-similar movies. `popularity_normalized` = weighted score ÷ highest weighted score in the dataset (0 for unrated movies). Weights live in `src/config.py`. |

**Reading the scores:** a similarity score (0-1) says how alike two movies are (by genre or by who rated them);
a popularity score is a weighted star rating; the hybrid score only ranks candidates against each other.
**None is a probability that you will enjoy a movie.** None of the models is personalised to a user.

**Cold start:** Content-based and Hybrid work for movies without ratings (they use genres). Collaborative
filtering cannot - the app tells you so and does **not** silently switch to another method.
Popularity ignores the selected movie except to leave it out of the list.

## Project structure

```
CineMatch/
├── app.py                     Streamlit entry point (page routing, cached model loading)
├── requirements.txt           Runtime dependencies
├── requirements-dev.txt       + pytest (and optional notebook packages, commented out)
├── pytest.ini                 Test configuration
├── .env.example               Optional settings (CINEMATCH_DATA_DIR)
├── .gitignore
├── .streamlit/config.toml     Dark theme
├── .vscode/                   settings.json, launch.json (run app / evaluation / tests)
├── data/                      Put the dataset here (see data/README.md)
├── notebooks/                 Original notebook (optional, for reference)
├── scripts/download_dataset.py  Safe dataset download / unzip helper
├── src/                       ML and data code - no Streamlit imports
│   ├── config.py              Paths, constants, weights
│   ├── utils.py               Exceptions and small helpers
│   ├── data_loader.py         Validation + loading of the CSV files
│   ├── preprocessing.py       Cleaning
│   ├── popularity_model.py  content_model.py  collaborative_model.py  hybrid_model.py
│   ├── recommender.py         Builds all models; one `recommend(method, movie_id, n)` call
│   ├── analytics.py           Statistics and catalogue filtering for the UI
│   └── evaluation.py          Offline evaluation (RMSE, Precision/Recall@10)
├── ui/                        Streamlit UI only: styles.py, components.py, pages.py
└── tests/                     pytest suite (uses tiny temporary datasets, no internet)
```

Differences from the suggested layout: added `src/recommender.py`, `src/analytics.py`, the `ui/` package,
`pytest.ini`, `.streamlit/config.toml` and `tests/test_evaluation.py`, `test_download_script.py`, `test_app_smoke.py`.

## Running the tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use small in-memory / temporary datasets and cover valid and invalid selections, count boundaries,
excluding the selected movie, duplicate prevention, missing/malformed/empty files, missing columns,
unrated movies, sparse data, the hybrid formula, ID/order consistency, the dataset zip helper, the
evaluation functions, and starting the Streamlit app (every page) headlessly.

## Evaluation

```powershell
python -m src.evaluation
```
(or use the **Run evaluation** button on the Model Insights page). It reports:

* **RMSE** of item-based collaborative-filtering *rating prediction* (80/20 split, seed 42, up to 3,000 test ratings) - same method as the notebook.
* **Precision@10 / Recall@10 of the popularity baseline only.** These do **not** evaluate the content-based, collaborative or hybrid recommenders.
  * *Original* (notebook): popularity list from **all** ratings (includes test data), first 100 users.
  * *Improved* (new): popularity from **training** ratings only, movies a user already rated in training are skipped, all users with a relevant held-out movie.

## Changes from the notebook

The algorithms and formulas are unchanged. Material implementation differences:

1. **Sparse throughout:** the collaborative matrix is built directly as a sparse matrix; the notebook built a dense `pivot_table` first. Matrix values are the same.
2. **Content similarity** is computed for the selected movie only (as the notebook's own `app.py` did) instead of a full N × N matrix. Cosine values are the same. **Ties** (very common with genre-only data) are broken by catalogue order, so results are deterministic; the notebook's tie order came from `np.argsort(...)[::-1]`.
3. **Movies are identified by `movieId`**, so duplicate titles are handled (the notebook looked up by title and took the first match). Duplicate titles get `[id N]` in the dropdown.
4. **Hybrid / popularity ties** use stable sorting (popularity ties by `movieId`).
5. **Extra display only:** collaborative results show cosine similarity (1 − distance); the notebook returned no score.
6. **Cleaning** additionally coerces ids/ratings to numbers and drops unparsable rows; `year` is parsed from the title.
7. `n_jobs=-1` was dropped from `NearestNeighbors`. The notebook's 3-method demo `app.py` is replaced by the 5-page app.
8. **Evaluation** was refactored into `src/evaluation.py` (same logic, no dense matrix, neighbour caching); the improved ranking evaluation is new and labelled as such.

I could not run the original notebook on the real dataset, so identical numbers (e.g. the exact RMSE) between notebook and project are **not** verified.

## Known limitations

* No movie posters (the dataset has none); no external API is used.
* The hybrid model re-ranks only the top 50 genre matches (as in the notebook). Because many movies share identical genres, that pool can contain arbitrary-but-equal candidates.
* Recommendations start from a movie; there are no user accounts or personalised profiles.
* MovieLens Small is small (~100k ratings), so collaborative results for rarely rated movies are weak.
* Built and tested (on Linux, Python 3.12) with streamlit 1.66.1, pandas 3.1.0, numpy 2.5.4, scikit-learn 1.9.1, scipy 1.18.1, altair 6.3.0; not run on Windows by me. The minimum versions in `requirements.txt` were not individually tested.

## Optional: the notebook

`notebooks/Movie Recomendation Code (1).ipynb` is the original development notebook, kept for reference.
It expects `data/movie dataset.zip`, contains Jupyter-only commands (`%%writefile`, `%pip`) and needs
`jupyter`, `matplotlib` and `seaborn` (see `requirements-dev.txt`). The app does not use it.
