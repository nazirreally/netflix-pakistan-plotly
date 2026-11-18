"""Filterable Netflix Pakistan research dashboard. Run: streamlit run app.py"""
import streamlit as st
from src.data import load_catalog, pakistan_titles, filter_titles, genre_counts, snapshot
from src.charts import (type_mix, yearly_additions, genres_bar, ratings_bar,
                        release_timeline, regional_comparison, coproductions, lead_time)

st.set_page_config(page_title="Netflix Pakistan | Content Intelligence",
                   page_icon="🎬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{--red:#e50914;--bg:#101115;--panel:#191b21}
html,body,.stApp{background:#101115;color:#f6f6f7}
[data-testid="stHeader"]{background:rgba(16,17,21,.8)}
[data-testid="stSidebar"]{background-color:#16181e;border-right:1px solid #292b32}
.block-container{padding-top:2rem;max-width:1460px}
h1,h2,h3{letter-spacing:-.035em}
.hero{border:1px solid #433039;border-radius:22px;padding:2.3rem;margin-bottom:1.4rem;
background:radial-gradient(ellipse at 94% 5%,rgba(229,9,20,.2),transparent 48%),linear-gradient(110deg,#242027,#16171c)}
.hero h1{font-size:clamp(2rem,4.2vw,3.7rem);line-height:1.08;color:#fff;margin:12px 0}
.hero h1 em{color:#ff4e55;font-style:normal}
.hero p{color:#c1c2ca;max-width:690px}
.eyebrow{font-size:.74rem;color:#f65c63;font-weight:800;letter-spacing:.16em}
.stat{background:#1a1b22;border:1px solid #303039;border-radius:17px;padding:1.2rem;min-height:110px}
.stat .num{font-size:2.3rem;font-weight:800;color:#fff;line-height:1.2}
.stat .name{font-size:.76rem;color:#a9abb4;text-transform:uppercase;letter-spacing:.09em;margin-top:.4rem}
[data-testid="stPlotlyChart"]{border:1px solid #303039;border-radius:16px;background:#17191e;overflow:hidden}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_data():
    return load_catalog()

try:
    full = get_data()
except (ValueError, FileNotFoundError) as exc:
    st.error(f"Unable to load catalogue: {exc}")
    st.stop()

pk = pakistan_titles(full)
baseline = snapshot(full)
with st.sidebar:
    st.title("🎬 Content Intelligence")
    st.caption("PAKISTAN EDITION · 2021 SNAPSHOT")
    st.divider()
    st.markdown("### Filter Pakistan-linked titles")
    kinds = st.multiselect("Format", ["Movie", "TV Show"], default=["Movie", "TV Show"])
    years = pk.release_year.dropna().astype(int)
    yr_range = st.slider("Release years", int(years.min()), int(years.max()),
                         (int(years.min()), int(years.max())))
    selected_genres = st.multiselect("Genres / categories",
                                    sorted(genre_counts(pk).genre.tolist()))
    ratings = st.multiselect("Ratings", sorted(pk.rating.dropna().unique().tolist()))
    st.divider()
    st.caption("Production-country credits are not streaming territory or local viewership.")
    st.caption("Historical source ends in September 2021.")

filtered = filter_titles(pk, types=kinds, release_range=yr_range,
                         genres=selected_genres, ratings=ratings)
st.markdown("""<div class="hero"><div class="eyebrow">N / ANALYTICS · PAKISTAN EDITION</div>
<h1>Streaming stories.<br><em>A Pakistani lens.</em></h1>
<p>Explore Pakistan-linked production credits in Netflix's historical global content catalogue.
Interactive Plotly charts, genre patterns and South Asian comparisons.</p>
<strong style="color:#ff777e;font-size:.8rem">HISTORICAL DATA THROUGH 25 SEP 2021 · NOT VIEWERSHIP DATA</strong></div>""",
unsafe_allow_html=True)
items = [(len(filtered), "Titles in current filter"),
         (int((filtered.type=="Movie").sum()), "Movies"),
         (int((filtered.type=="TV Show").sum()), "TV shows"),
         (int(filtered.is_coproduction.sum()), "Co-productions")]
for column,(value,label) in zip(st.columns(4),items):
    column.markdown(f'<div class="stat"><div class="num">{value}</div><div class="name">{label}</div></div>',
                    unsafe_allow_html=True)
st.caption(f"Unfiltered source: {baseline['pakistan_titles']} Pakistan-linked titles of {baseline['global_titles']:,} global records.")
t1,t2,t3,t4 = st.tabs(["📊 Pakistan deep dive","🌏 South Asia","🎞️ Explore titles","ℹ️ Methods"])
with t1:
    if filtered.empty:
        st.warning("No records match your filters.")
    else:
        pairs = [(type_mix,yearly_additions),(genres_bar,ratings_bar),
                 (release_timeline,coproductions)]
        for fn1,fn2 in pairs:
            a,b=st.columns(2)
            with a: st.plotly_chart(fn1(filtered), use_container_width=True)
            with b: st.plotly_chart(fn2(filtered), use_container_width=True)
        st.plotly_chart(lead_time(filtered), use_container_width=True)
        st.info("Genres may overlap, and catalogue addition dates are not release dates.")
with t2:
    st.subheader("South Asian production credits")
    st.plotly_chart(regional_comparison(full),use_container_width=True)
    st.caption("Unfiltered counts. Multiple credited countries can be counted for one title.")
with t3:
    st.subheader("The source records")
    query=st.text_input("Search titles",placeholder="e.g. Cake, Humsafar")
    listing=filtered
    if query:
        listing=listing.loc[listing.title.str.contains(query,case=False,regex=False,na=False)]
    table=(listing[["title","type","release_year","added_year","rating","country","listed_in"]]
           .rename(columns={"title":"Title","type":"Format","release_year":"Released",
                            "added_year":"Added","rating":"Rating","country":"Production credits",
                            "listed_in":"Categories"}))
    st.dataframe(table,use_container_width=True,hide_index=True)
    st.download_button("Download filtered CSV",table.to_csv(index=False).encode("utf-8"),
                       file_name="netflix_pakistan_filtered.csv",mime="text/csv")
with t4:
    st.markdown("""
### Definitions and caveats
- **Source:** Netflix Movies and TV Shows, Kaggle (8,807 rows; last addition September 25, 2021).
- **Pakistan-linked:** a literal 'Pakistan' token in the production country field.
- **Co-productions:** counted for each credited country; totals can overlap.
- **Categories:** Netflix 'listed_in' labels are multi-valued.
- **Missing metadata:** blank country information cannot prove that a title is non-Pakistani.
- **Interpretation:** this dataset has no Pakistani subscriber, watching, rights, or revenue data.
- **Small sample:** 24 Pakistan-linked records support descriptive analysis, not forecasting.
""")
st.divider()
st.caption("N / ANALYTICS · Nazir Ali Khan · Independent educational project, unaffiliated with Netflix.")
