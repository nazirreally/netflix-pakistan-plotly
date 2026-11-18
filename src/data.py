"""Auditable Netflix catalogue transformations.

The country column identifies production credits, never subscriber location,
streaming availability, popularity, or audience size.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "netflix_titles.csv"
SOUTH_ASIA = ("India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka", "Afghanistan", "Bhutan", "Maldives")
REQUIRED = {"show_id", "type", "title", "country", "date_added", "release_year", "rating", "duration", "listed_in"}


def labels(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def load_catalog(path=DEFAULT_DATA) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {sorted(missing)}")
    if data.show_id.duplicated().any():
        raise ValueError("Duplicate show_id values in source")
    data = data.copy()
    for col in ("title", "type", "country", "listed_in", "rating"):
        data[col] = data[col].astype("string").str.strip()
    data["production_countries"] = data.country.map(labels)
    data["genres"] = data.listed_in.map(labels)
    data["added_at"] = pd.to_datetime(data.date_added.astype("string").str.strip(), errors="coerce", format="mixed")
    data["added_year"] = data.added_at.dt.year.astype("Int64")
    data["release_year"] = pd.to_numeric(data.release_year, errors="coerce").astype("Int64")
    data["is_pakistan"] = data.production_countries.map(lambda x: "Pakistan" in x)
    data["is_coproduction"] = data.is_pakistan & data.production_countries.map(lambda x: len(x)>1)
    data["catalog_lag_years"] = data.added_year - data.release_year
    return data


def pakistan_titles(df):
    return df.loc[df.is_pakistan].copy()


def regional_counts(df, countries=SOUTH_ASIA):
    credits = df[["show_id", "production_countries"]].explode("production_countries")
    counts = credits.groupby("production_countries").show_id.nunique()
    return pd.DataFrame({"country": list(countries), "titles": [int(counts.get(c, 0)) for c in countries]})


def genre_counts(df, top_n=None):
    credits = df[["show_id", "genres"]].explode("genres").dropna(subset=["genres"])
    counts = (credits.groupby("genres").show_id.nunique().sort_values(ascending=False)
              .rename_axis("genre").reset_index(name="titles"))
    return counts.head(top_n) if top_n else counts


def annual_additions(df):
    result = (df.dropna(subset=["added_year"]).groupby(["added_year", "type"])
              .size().reset_index(name="titles"))
    return result.sort_values("added_year")


def filter_titles(df, *, types=None, release_range=None, genres=None, ratings=None):
    out = df
    if types is not None:
        out = out.loc[out.type.isin(types)]
    if release_range is not None:
        out = out.loc[out.release_year.between(*release_range)]
    if genres:
        selected = set(genres)
        out = out.loc[out.genres.map(lambda values: bool(selected.intersection(values)))]
    if ratings:
        out = out.loc[out.rating.isin(ratings)]
    return out.copy()


def snapshot(df):
    pk = pakistan_titles(df)
    return {"global_titles": len(df), "pakistan_titles": len(pk),
            "movies": int((pk.type=="Movie").sum()), "tv_shows": int((pk.type=="TV Show").sum()),
            "coproductions": int(pk.is_coproduction.sum()), "distinct_genres": len(genre_counts(pk))}
