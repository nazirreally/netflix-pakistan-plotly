"""Reusable Plotly figures in the Netflix-inspired dark analytics theme."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data import genre_counts, annual_additions, regional_counts

RED, ORANGE = "#e50914", "#ff9868"
BG, PANEL = "#101115", "#17191e"
PALETTE = [RED, "#ff7648", "#eeaa66", "#a1a2ab", "#6b7280", "#ffd9bd"]


def polish(fig, height=370, legend=True):
    fig.update_layout(template="plotly_dark", paper_bgcolor=PANEL, plot_bgcolor=PANEL,
                      font=dict(family="Inter, Arial, sans-serif", color="#f4f4f5", size=12),
                      height=height, margin=dict(l=18,r=18,t=50,b=32),
                      colorway=PALETTE, showlegend=legend,
                      legend=dict(orientation="h",x=0,y=1.14,bgcolor="rgba(0,0,0,0)"),
                      hoverlabel=dict(bgcolor="#282b34",font_color="#fff"),
                      xaxis=dict(showgrid=True,gridcolor="#292c33",zeroline=False),
                      yaxis=dict(showgrid=False,zeroline=False))
    return fig


def type_mix(df):
    counts = df.type.value_counts().rename_axis("type").reset_index(name="titles")
    fig = (px.pie(counts,names="type",values="titles",hole=.68,color="type",
           color_discrete_map={"Movie":RED,"TV Show":ORANGE}) if len(counts) else go.Figure())
    fig.update_traces(textposition="outside",textinfo="label+value",sort=False,
                      marker=dict(line=dict(color=PANEL,width=3)))
    fig = polish(fig,legend=False)
    fig.update_layout(title="Content mix")
    return fig


def yearly_additions(df):
    fig = px.bar(annual_additions(df),x="added_year",y="titles",color="type",barmode="stack",
                 color_discrete_map={"Movie":RED,"TV Show":ORANGE},
                 labels={"added_year":"Year added","titles":"Titles","type":"Format"})
    fig=polish(fig)
    fig.update_layout(title="When titles entered the catalogue",xaxis=dict(dtick=1,showgrid=False))
    return fig


def genres_bar(df):
    counts=genre_counts(df,10).sort_values("titles")
    fig=px.bar(counts,x="titles",y="genre",orientation="h",text="titles",
               labels={"titles":"Titles","genre":""})
    fig.update_traces(marker_color=RED,textposition="outside",cliponaxis=False)
    fig=polish(fig,height=440,legend=False)
    fig.update_layout(title="Genres & categories",margin=dict(l=12,r=50,t=48,b=28))
    return fig


def ratings_bar(df):
    counts=df.rating.fillna("Not recorded").value_counts().rename_axis("rating").reset_index(name="titles")
    fig=px.bar(counts,x="rating",y="titles",text="titles")
    fig.update_traces(marker_color=ORANGE,textposition="outside")
    fig=polish(fig,legend=False)
    fig.update_layout(title="Content classifications",xaxis_title="Rating")
    return fig


def release_timeline(df):
    counts=df.groupby("release_year").size().reset_index(name="titles").dropna()
    fig=px.bar(counts,x="release_year",y="titles",text="titles")
    fig.update_traces(marker_color=RED,textposition="outside")
    fig=polish(fig,legend=False)
    fig.update_layout(title="Original release years",xaxis_title="Year",xaxis=dict(dtick=2,showgrid=False))
    return fig


def coproductions(df):
    counts=df.is_coproduction.map({False:"Pakistan only",True:"International co-production"}).value_counts()
    fig=px.pie(names=counts.index.tolist(),values=counts.values.tolist(),hole=.62,
               color=counts.index.tolist(),color_discrete_map={"Pakistan only":RED,"International co-production":ORANGE})
    fig.update_traces(textinfo="label+value",textposition="outside")
    fig=polish(fig,legend=False)
    fig.update_layout(title="Pakistan-only vs co-produced")
    return fig


def lead_time(df):
    counts=(df.loc[df.catalog_lag_years.between(0,60),"catalog_lag_years"]
            .value_counts().rename_axis("lag").reset_index(name="titles").sort_values("lag"))
    fig=px.bar(counts,x="lag",y="titles",text="titles")
    fig.update_traces(marker_color=ORANGE,textposition="outside")
    fig=polish(fig,legend=False)
    fig.update_layout(title="Release to catalogue-addition lag",xaxis_title="Approx. calendar years")
    return fig


def regional_comparison(df):
    counts=regional_counts(df)
    counts=counts.loc[counts.titles>0].sort_values("titles")
    counts["label"]=counts.titles.map(lambda n:f"{n:,}")
    fig=px.bar(counts,x="titles",y="country",orientation="h",text="label")
    fig.update_traces(marker_color=[RED if c=="Pakistan" else "#6d727d" for c in counts.country],
                      textposition="outside",cliponaxis=False)
    fig=polish(fig,height=420,legend=False)
    fig.update_layout(title="South Asian production-country credits",
                      xaxis_title="Titles (log scale)",xaxis_type="log",yaxis_title="",
                      margin=dict(l=16,r=65,t=50,b=45))
    return fig
