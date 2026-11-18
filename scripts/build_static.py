"""Generate the offline interactive Plotly site from the pinned CSV.

Commands:
  python scripts/build_static.py
  python scripts/build_static.py --verify
"""
from __future__ import annotations
from pathlib import Path
import argparse
import html
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from plotly.io import to_html
from plotly.offline.offline import get_plotlyjs
from src.data import load_catalog, pakistan_titles, snapshot, regional_counts
from src.charts import (type_mix,yearly_additions,genres_bar,ratings_bar,
                        release_timeline,coproductions,lead_time,regional_comparison)

DOCS=ROOT/"docs"
CARDS=[
 ("01 / FORMAT MIX",type_mix,"20 movies and 4 TV series in the source."),
 ("02 / CATALOGUE TIMELINE",yearly_additions,"Year added to global catalogue, not release date."),
 ("03 / CATEGORY SIGNAL",genres_bar,"Genres overlap: a title may appear in multiple categories."),
 ("04 / MATURITY RATINGS",ratings_bar,"Content classifications, not audience review scores."),
 ("05 / RELEASE YEARS",release_timeline,"Original production release years."),
 ("06 / INTERNATIONAL CREDITS",coproductions,"Co-produced titles credit multiple countries."),
 ("07 / CONTENT AGE",lead_time,"Difference of calendar years; not viewing delay."),
]
STYLE=r"""
:root{--bg:#101115;--panel:#191b20;--border:#303039;--white:#f5f5f7;--soft:#afb1bc;--red:#e50914}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--white);font:15px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}
a{color:#ff8288;text-decoration:none}a:hover{text-decoration:underline}
.shell{width:min(1400px,93%);margin:auto}
.top{display:flex;justify-content:space-between;align-items:center;gap:1em;padding:24px 0;border-bottom:1px solid #292b32}
.brand{font-weight:900;letter-spacing:.075em}.brand b{color:var(--red)}
.nav{display:flex;gap:2em;flex-wrap:wrap}.nav a{font-size:.8rem;color:#cdced5}
.hero{padding:72px 50px 58px;margin:32px 0 24px;border:1px solid #45323b;border-radius:25px;
background:radial-gradient(ellipse at 92% 4%,rgba(229,9,20,.22),transparent 45%),linear-gradient(115deg,#292029,#17181e);position:relative;overflow:hidden}
.hero:after{content:'N';position:absolute;right:2%;top:-150px;font-size:630px;line-height:1;font-weight:900;color:#e50914;opacity:.06;pointer-events:none}
.eyebrow{font-size:.74rem;letter-spacing:.17em;color:#ff777e;font-weight:800}
.hero h1{font-size:clamp(44px,5.5vw,80px);letter-spacing:-.06em;line-height:1.08;margin:17px 0}
.hero h1 em{font-style:normal;color:#ff525a}.hero p{color:#c2c3ca;max-width:720px;font-size:1.04rem}
.tag{display:inline-block;border:1px solid #614149;color:#ffc1c7;border-radius:50px;margin:12px 10px 0 0;padding:6px 13px;font-size:.7rem;letter-spacing:.08em}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:25px 0 32px}
.metric{border:1px solid var(--border);border-radius:17px;background:#1b1c23;padding:24px}
.metric span{color:#afb0b9;font-size:.74rem;text-transform:uppercase;letter-spacing:.08em}
.metric strong{display:block;font-size:48px;margin:10px 0;letter-spacing:-.05em;line-height:1.1}
.metric small{color:#9497a1;font-size:.78rem}
.warning{border:1px solid #624047;border-left:4px solid var(--red);border-radius:12px;background:#26191e;padding:20px 24px;color:#dfd7da;margin:25px 0 46px}
.chapter{margin:55px 0 25px}.chapter h2{font-size:clamp(26px,3vw,40px);letter-spacing:-.04em;margin:5px 0}
.chapter p{color:var(--soft);max-width:780px;margin:3px 0}
.visuals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.visual{background:var(--panel);border:1px solid var(--border);border-radius:20px;min-width:0;padding:18px 12px 10px;overflow:hidden}
.visual-label{font-size:.68rem;color:#ff858b;letter-spacing:.13em;font-weight:800;margin:0 12px 5px}
.visual-note{font-size:.75rem;color:#9699a2;margin:0 12px 5px;min-height:32px}
.wide{grid-column:1/-1}.plotly-graph-div{width:100%!important}
.insight{background:#1d2026;border-radius:14px;border:1px solid #33343c;padding:18px 23px;margin:20px 0;color:#d8d8dc}
.search{background:#1e2026;border:1px solid #55545c;border-radius:10px;padding:13px 15px;color:#fff;width:min(420px,100%);font:inherit;margin:12px 0 16px}
.count{margin-left:12px;color:#a2a3aa;font-size:.82rem}
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:14px}
table{width:100%;border-collapse:collapse;font-size:.81rem}thead{background:#282831;color:#d1d1d6}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid #303037;white-space:nowrap}
td:last-child{white-space:normal;min-width:240px}td:first-child{font-weight:800}
th{text-transform:uppercase;font-size:.7rem;letter-spacing:.07em}
.method{background:#1a1c22;border:1px solid var(--border);padding:23px;border-radius:16px;color:#c0c1ca}
.method li{padding:4px 0}
footer{margin-top:55px;padding:28px 0 55px;border-top:1px solid #33353b;color:#9395a0;font-size:.8rem}
@media(max-width:850px){.metrics{grid-template-columns:repeat(2,1fr)}.visuals{grid-template-columns:1fr}.hero{padding:50px 25px}.top{align-items:flex-start;flex-direction:column;gap:.4em}}
@media(max-width:500px){.metric{padding:17px}.metric strong{font-size:37px}.tag{font-size:.6rem}}
"""


def chart_html(fig, name, note):
    plot=to_html(fig,full_html=False,include_plotlyjs=False,
                 config={"displaylogo":False,"responsive":True,
                         "modeBarButtonsToRemove":["lasso2d","select2d"]})
    return (f'<article class="visual"><div class="visual-label">{html.escape(name)}</div>'
            f'{plot}<p class="visual-note">{html.escape(note)}</p></article>')


def build():
    full=load_catalog()
    pk=pakistan_titles(full)
    stats=snapshot(full)
    credits=regional_counts(full).set_index("country").titles
    first=[chart_html(fun(pk),name,note) for name,fun,note in CARDS]
    last=chart_html(regional_comparison(full),"08 / SOUTH ASIAN COMPARISON",
                    "Production-country credits, not available titles or local viewing.")
    rows=[]
    for _,item in pk.sort_values("title",key=lambda s:s.str.lower()).iterrows():
        vals=[item.title,item.type,int(item.release_year),item.rating,item.country,item.listed_in]
        rows.append("<tr>"+"".join(f"<td>{html.escape(str(v))}</td>" for v in vals)+"</tr>")
    metrics=[
        ("Pakistan-linked titles",stats["pakistan_titles"],f"Of {stats['global_titles']:,} global records"),
        ("Movies",stats["movies"],"83% of Pakistan-linked titles"),
        ("TV series",stats["tv_shows"],"17% of Pakistan-linked titles"),
        ("Co-productions",stats["coproductions"],"Multiple production-country credits"),
    ]
    metrics_html='<div class="metrics">'+''.join(
        f'<div class="metric"><span>{a}</span><strong>{b}</strong><small>{c}</small></div>'
        for a,b,c in metrics)+'</div>'
    page=r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Pakistan-linked Netflix production titles in historical global catalogue with 8 interactive Plotly charts.">
<meta name="theme-color" content="#101115"><title>Netflix Pakistan | Content Intelligence</title>
<script src="assets/plotly.min.js"></script><style>__STYLE__</style></head><body>
<div class="shell"><header class="top"><div class="brand"><b>N</b> / CONTENT INTELLIGENCE</div>
<nav class="nav"><a href="#overview">OVERVIEW</a><a href="#visuals">VISUALS</a>
<a href="#titles">TITLES</a><a href="#method">METHODS</a></nav></header>
<section class="hero" id="overview"><div class="eyebrow">NETFLIX · PAKISTAN EDITION · DATA STORY</div>
<h1>Streaming stories.<br><em>A Pakistani lens.</em></h1>
<p>What do Netflix's historical worldwide records reveal about Pakistani-produced
movies and TV? Explore release patterns, genres and South Asian comparisons.</p>
<span class="tag">HISTORICAL TO SEP 2021</span><span class="tag">8,807 RECORDS</span>
<span class="tag">PYTHON + PLOTLY</span></section>
__METRICS__
<div class="warning"><strong>Data boundary:</strong> Country denotes credited production country,
not availability in Pakistan, audience preferences, regional subscribers, or current streaming titles.</div>
<section class="chapter" id="visuals"><div class="eyebrow">01 / PAKISTAN DEEP DIVE</div>
<h2>Unpack the 24-title footprint.</h2><p>Eight interactive Plotly charts:
hover, zoom and export visualizations. Descriptive analysis only.</p></section>
<div class="visuals">__FIRST__</div>
<section class="chapter"><div class="eyebrow">02 / REGIONAL CONTEXT</div>
<h2>A South Asian comparison.</h2><p>Log-scale display for small country counts.
Multi-country titles can appear in more than one bar.</p></section>
<div class="visuals">__LAST__</div>
<div class="insight">This source credits India with <b>__INDIA__</b> titles and Pakistan
with <b>__PAKISTAN__</b>. These are catalogue production credits, not market share or demand.</div>
<section class="chapter" id="titles"><div class="eyebrow">03 / SOURCE RECORDS</div>
<h2>Browse every credited Pakistani title.</h2><p>Search the underlying 24 records.</p></section>
<input class="search" id="search" type="search" placeholder="Find a title, genre, country or rating"
aria-label="Search Pakistani titles"><span class="count" id="count">24 matching titles</span>
<div class="table-wrap"><table id="titles-table"><thead><tr><th>Title</th><th>Format</th>
<th>Release</th><th>Rating</th><th>Country</th><th>Genres</th></tr></thead>
<tbody>__ROWS__</tbody></table></div>
<section class="chapter" id="method"><div class="eyebrow">04 / METHODOLOGY</div><h2>How to read this data.</h2></section>
<div class="method"><ul><li>Source: <a href="https://www.kaggle.com/datasets/shivamb/netflix-shows">Netflix Movies and TV Shows (Kaggle)</a>; additions through September 25, 2021.</li>
<li>The production country field is comma-separated; 'Pakistan' is matched as an exact token.</li>
<li>Each multi-country production is counted for each credited country, not exclusively.</li>
<li>Categories and genres can overlap; label totals need not equal unique title counts.</li>
<li>Missing countries are unknown; content ratings are classifications rather than reviews.</li>
<li>No Netflix Pakistan viewership, subscriber, availability or revenue data is present.</li>
<li>Source transformations, chart definitions, and reproduction scripts are included in the <a href="https://github.com/nazirreally/netflix-pakistan-plotly">GitHub repository</a>.</li></ul></div>
<footer>Netflix Pakistan · Independent research project by Nazir Ali Khan · Unaffiliated with Netflix</footer></div>
<script>
const q=document.querySelector("#search"),trs=[...document.querySelectorAll("#titles-table tbody tr")];
q.addEventListener("input",()=>{let n=0;for(const tr of trs){
let on=tr.textContent.toLowerCase().includes(q.value.toLowerCase().trim());
tr.hidden=!on;if(on)n++}
document.querySelector("#count").textContent=n+" matching title"+(n===1?"":"s")});
</script></body></html>"""
    for a,b in {
        "__STYLE__":STYLE,
        "__METRICS__":metrics_html,
        "__FIRST__":"\n".join(first),
        "__LAST__":last,
        "__INDIA__":f"{int(credits.get('India',0)):,}",
        "__PAKISTAN__":f"{int(credits.get('Pakistan',0)):,}",
        "__ROWS__":"\n".join(rows),
    }.items():
        page=page.replace(a,b)
    (DOCS/"assets").mkdir(parents=True,exist_ok=True)
    (DOCS/"index.html").write_text(page,encoding="utf-8")
    (DOCS/"assets"/"plotly.min.js").write_text(get_plotlyjs(),encoding="utf-8")
    svg='''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600">
<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#241b23"/><stop offset="1" stop-color="#111217"/></linearGradient></defs>
<rect width="1200" height="600" fill="url(#bg)"/>
<rect x="46" y="46" width="1108" height="508" rx="24" fill="none" stroke="#564048"/>
<text x="85" y="118" font-family="Arial" font-weight="bold" font-size="23" fill="#ff767f">N / CONTENT INTELLIGENCE</text>
<text x="85" y="229" font-family="Arial" font-weight="bold" font-size="78" fill="#ffffff">Streaming stories.</text>
<text x="85" y="321" font-family="Arial" font-weight="bold" font-size="78" fill="#ff4b55">A Pakistani lens.</text>
<text x="85" y="389" font-family="Arial" font-size="24" fill="#c2c3c9">Historical Netflix production-country credits · Plotly analytics</text>
<text x="85" y="483" font-family="Arial" font-weight="bold" font-size="54" fill="#ffffff">24</text>
<text x="235" y="483" font-family="Arial" font-weight="bold" font-size="54" fill="#ffffff">20</text>
<text x="385" y="483" font-family="Arial" font-weight="bold" font-size="54" fill="#ffffff">4</text>
<text x="85" y="514" font-family="Arial" font-size="17" fill="#b9bbc1">TITLES</text>
<text x="235" y="514" font-family="Arial" font-size="17" fill="#b9bbc1">MOVIES</text>
<text x="385" y="514" font-family="Arial" font-size="17" fill="#b9bbc1">TV SHOWS</text>
</svg>'''
    (DOCS/"assets"/"preview.svg").write_text(svg,encoding="utf-8")
    print(f"Built {DOCS/'index.html'} ({len(page):,} chars), Plotly.js and preview SVG")


def verify():
    source=load_catalog()
    assert snapshot(source)["pakistan_titles"]==24
    page=(DOCS/"index.html").read_text(encoding="utf-8")
    assert page.count("plotly-graph-div")>=8
    assert page.count("<tr>")==25
    assert "24 matching titles" in page
    assert (DOCS/"assets"/"plotly.min.js").stat().st_size>1_000_000
    assert (DOCS/"assets"/"preview.svg").exists()
    print("Static report verified: 8 Plotly charts, 24 titles, offline library")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    verify() if args.verify else build()
