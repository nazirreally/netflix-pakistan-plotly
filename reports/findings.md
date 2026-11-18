# Netflix Pakistan — verified historical findings

**Dataset:** 8,807 Netflix title metadata records (Kaggle Netflix Movies and TV Shows).
The last catalogue addition date is **2021-09-25**. All figures describe
that historical dataset, **not** current availability or Netflix Pakistan viewership.

| Metric | Count | Interpretation |
|---|---:|---|
| Global title records | 8,807 | Size of historical source |
| Pakistan production-country credits | 24 | Exact Pakistan country token |
| Pakistan-linked movies | 20 | 83.3% of Pakistan cohort |
| Pakistan-linked TV shows | 4 | 16.7% |
| International co-productions | 6 | Titles crediting 2+ countries |
| Distinct genre/category labels | 13 | Multi-label categories |
| International Movies mentions | 19 | Genres can overlap |
| Dramas mentions | 13 | Separate from TV Dramas |
| Pakistan-linked titles added in 2019 | 9 | Addition date, not release date |
| India production credits | 1,046 | Multi-credit count |
| Bangladesh / Nepal / Sri Lanka credits | 4 / 2 / 1 | Small source subsets |

## Pakistan timeline

The historical addition-year counts for Pakistan-linked titles are:
2016 (4), 2017 (5), 2018 (5), 2019 (9) and 2020 (1).
No Pakistan-linked source row has a 2021 addition date.

## Limitations

1. Production-country metadata is **not** a measure of Netflix Pakistan streaming rights, audience interests, subscribers or demand.
2. The Pakistan cohort is very small (24 records); avoid statistical forecasts.
3. Production country is absent for **831** of 8,807 source rows. Missing is not non-Pakistani.
4. A multi-country production appears in multiple regional bars.
5. Genre labels overlap; counts are not mutually exclusive.
6. Ratings are content classifications, not user review ratings.
7. Catalogue data ends in 2021 and cannot describe November 2026 availability.

## Reproduce

    pip install -r requirements-dev.txt
    pytest -q
    python scripts/build_static.py
    python scripts/build_static.py --verify
    streamlit run app.py

Inspiration: [Plotly Netflix Kaggle notebook](https://www.kaggle.com/code/rushikeshdane20/in-depth-analysis-of-netflix-with-plotly).
This project's analysis, code, and graphics are independently developed.
