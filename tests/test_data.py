"""Tests rely on the pinned historical 8,807-row Netflix source."""
from src.data import load_catalog, pakistan_titles, snapshot, labels, regional_counts, genre_counts
from src.charts import (type_mix, yearly_additions, genres_bar, ratings_bar,
                        release_timeline, regional_comparison, coproductions, lead_time)


def test_exact_country_token():
    assert labels("Pakistan, United States") == ["Pakistan", "United States"]
    assert "Pakistan" not in labels("Other Pakistani country")


def test_source_size_and_selection():
    full=load_catalog()
    assert len(full)==8807
    assert len(pakistan_titles(full))==24
    assert full.show_id.is_unique
    assert full.country.isna().sum()==831


def test_country_and_format_metrics():
    facts=snapshot(load_catalog())
    assert facts["movies"]==20 and facts["tv_shows"]==4
    assert facts["coproductions"]==6
    assert facts["distinct_genres"]==13


def test_regional_credits():
    regional=regional_counts(load_catalog()).set_index("country").titles
    assert regional["Pakistan"]==24
    assert regional["India"]==1046


def test_multi_label_categories():
    pk=pakistan_titles(load_catalog())
    genres=genre_counts(pk).set_index("genre").titles
    assert genres["International Movies"]==19
    assert genres["Dramas"]==13


def test_charts_render():
    full=load_catalog()
    pk=pakistan_titles(full)
    charts=[type_mix(pk), yearly_additions(pk), genres_bar(pk), ratings_bar(pk),
            release_timeline(pk), coproductions(pk), lead_time(pk), regional_comparison(full)]
    assert len(charts)==8
    assert all(len(chart.to_json())>100 for chart in charts)
