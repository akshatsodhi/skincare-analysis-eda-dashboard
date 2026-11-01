"""Beauty Intelligence | Executive-grade interactive EDA based on the supplied notebook.

Launch with: streamlit run app.py
Requires the separate source dataset (project.xlsx), not embedded in the notebook.
"""
from __future__ import annotations

import io
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Beauty Intelligence | Boardroom", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
EXPECTED = ["Product_Name", "Brand", "Category", "Usage_Frequency", "Price_USD", "Rating", "Number_of_Reviews", "Product_Size", "Skin_Type", "Gender_Target", "Packaging_Type", "Main_Ingredient", "Cruelty_Free", "Country_of_Origin"]
C = {"ink":"#0B131D", "surface":"#142231", "gold":"#B7925B", "teal":"#58B8AE", "ivory":"#EAF1F4", "muted":"#9EAEB9", "grid":"#2B3945", "blue":"#738FB6"}
COLORS = [C["teal"], C["gold"], C["blue"], "#D2A28B", "#A18DC1", "#77A6A9", "#D0BD8B"]

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],p,div,span{font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.035em!important}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 82% -3%,#162b37 0%,#0b131d 54%);}
[data-testid="stSidebar"]{background:#0E1B28;border-right:1px solid #273440}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1540px;padding-top:2.5rem;padding-bottom:4rem}
#MainMenu,footer{visibility:hidden}
.eyebrow{color:#B7925B;font-size:.76rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;margin-bottom:.7rem}
.hero{border:1px solid #31404a;border-radius:19px;padding:2rem 2.2rem;background:linear-gradient(115deg,rgba(35,63,72,.84),rgba(18,32,46,.62));margin-bottom:1.4rem}
.hero h1{font-size:2.8rem!important;margin:.1rem 0 .65rem!important;color:#F5F0E6!important}
.hero p{font-size:1.01rem;color:#B9CAD0;max-width:900px;line-height:1.8;margin:0}
.metric{padding:1.2rem 1.25rem;background:linear-gradient(140deg,#172938,#10202e);border:1px solid #2c3d4b;border-radius:14px;min-height:116px}
.metric-label{color:#9BAFBC;font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;font-weight:700}
.metric-value{font-size:2rem;letter-spacing:-.05em;font-weight:800;color:#F4F1E8;padding-top:.7rem;line-height:1.15}
.metric-foot{font-size:.76rem;color:#91A8B4;margin-top:.5rem}
.section-head{margin:1.8rem 0 .6rem;color:#F2EEE7;font-size:1.2rem;font-weight:800;letter-spacing:-.03em}
.insight{border-left:3px solid #B7925B;background:#142330;border-radius:0 12px 12px 0;padding:1.15rem 1.4rem;margin:.85rem 0;color:#CEDDE1;line-height:1.7}
.micro{font-size:.84rem;color:#A3B3BD;line-height:1.65}
[data-testid="stPlotlyChart"]{border:1px solid #263746;border-radius:14px;background:#101E2B;padding:.2rem .35rem}
[data-testid="stDataFrame"]{border:1px solid #2a3947;border-radius:12px}
div[data-testid="stRadio"] label{padding:.2rem 0}
[data-testid="stMetricLabel"]{color:#9BAFBC}
hr{border-color:#283845!important}
</style>''', unsafe_allow_html=True)


def clean(df:pd.DataFrame)->pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    for c in EXPECTED:
        if c not in df.columns:
            df[c] = np.nan
    for c in ["Product_Name", "Brand", "Category", "Usage_Frequency", "Skin_Type", "Gender_Target", "Packaging_Type", "Main_Ingredient", "Country_of_Origin"]:
        df[c] = df[c].astype("string").str.strip().replace("",pd.NA).fillna("Unknown")
    for c in ("Price_USD", "Rating", "Number_of_Reviews"):
        df[c] = pd.to_numeric(df[c],errors="coerce")
    df["Product_Size_Numeric"] = pd.to_numeric(df["Product_Size"].astype("string").str.extract(r"([-+]?\d*\.?\d+)")[0],errors="coerce")
    v = df["Cruelty_Free"].astype("string").str.strip().str.lower()
    mapping={"true":"Yes","1":"Yes","yes":"Yes","y":"Yes","false":"No","0":"No","no":"No","n":"No"}
    df["Cruelty_Label"] = v.map(mapping).fillna("Unknown")
    # Keep notebook's fixed price thresholds; do not silently drop out-of-range products.
    df["Price_Band"] = pd.cut(df["Price_USD"],bins=[0,20,50,100,500],labels=["Low · $0–20","Mid · $20–50","High · $50–100","Premium · $100–500"],include_lowest=True)
    df["Price_Band"] = df["Price_Band"].astype("object").fillna("Outside bands / unknown")
    median_size=df["Product_Size_Numeric"].median()
    df["Size_Class"] = np.where(df["Product_Size_Numeric"].isna(),"Unknown",np.where(df["Product_Size_Numeric"] >= median_size,"Large","Small")) if pd.notna(median_size) else "Unknown"
    return df

@st.cache_data(show_spinner=False)
def read_file(blob:bytes,name:str)->pd.DataFrame:
    if name.lower().endswith(".csv"):
        raw=pd.read_csv(io.BytesIO(blob))
    else:
        raw=pd.read_excel(io.BytesIO(blob))
    return clean(raw)


def plot_style(fig,height=370,percent=False):
    fig.update_layout(height=height,margin=dict(l=16,r=18,t=36,b=35),paper_bgcolor="#101E2B",plot_bgcolor="#101E2B",font=dict(family="DM Sans",color=C["ivory"],size=12),hoverlabel=dict(bgcolor="#253745",font_color="#FFFFFF"),legend=dict(orientation="h",yanchor="bottom",y=1.03,x=0),colorway=COLORS)
    fig.update_xaxes(showgrid=False,zeroline=False,showline=False,tickfont=dict(color=C["muted"]))
    fig.update_yaxes(showgrid=True,gridcolor=C["grid"],zeroline=False,tickfont=dict(color=C["muted"]))
    return fig


def metric(label,value,foot=""):
    st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',unsafe_allow_html=True)


def bar(data,x,y,title,orientation="h",height=370,color=None):
    if data.empty:
        st.info("No data for this selection.");return
    fig=px.bar(data,x=x,y=y,orientation=orientation,color=color,color_discrete_sequence=COLORS,text_auto=False)
    if color is None:fig.update_traces(marker_color=C["teal"])
    fig.update_layout(title=dict(text=title,font=dict(size=15)),showlegend=color is not None)
    if orientation=="h":fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(plot_style(fig,height),use_container_width=True,config={"displaylogo":False})


def hdr(title,subtitle=None):
    st.markdown(f'<div class="section-head">{title}</div>',unsafe_allow_html=True)
    if subtitle:st.markdown(f'<div class="micro">{subtitle}</div>',unsafe_allow_html=True)


def insight(text):st.markdown(f'<div class="insight">{text}</div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="eyebrow">◈ BEAUTY INTELLIGENCE</div>',unsafe_allow_html=True)
    st.caption("MARKET & PORTFOLIO ANALYTICS")
    st.markdown("---")
    file=st.file_uploader("Source dataset",type=["xlsx","xls","csv"],help="Upload the project.xlsx used by the original notebook.")
    local=next((p for p in (ROOT/"project.xlsx", ROOT/"project.csv") if p.exists()),None)
    if file:
        raw_bytes=file.getvalue(); source_name=file.name
    elif local:
        raw_bytes=local.read_bytes();source_name=local.name
    else:
        raw_bytes=None;source_name=None

if raw_bytes is None:
    st.markdown('<div class="hero"><div class="eyebrow">BOARDROOM / RESEARCH SERIES 01</div><h1>Beauty Industry Intelligence</h1><p>A structured view of the beauty product landscape: positioning, product assortment, consumer feedback signals and attribute-level comparisons.</p></div>',unsafe_allow_html=True)
    st.info("**Connect the dataset to begin.** Upload the original `project.xlsx` (or CSV) using the left sidebar, or place it alongside `app.py`. The notebook references this file but does not embed the complete dataset.")
    hdr("What the dashboard will cover")
    c1,c2,c3=st.columns(3)
    with c1:metric("01 / Overview","Portfolio","Product mix · KPIs · geography")
    with c2:metric("02 / Performance","Brands","Ratings · reviews · price tiers")
    with c3:metric("03 / Deep dive","Attributes","Ingredients · skin · packaging")
    st.markdown('<div class="micro">This dashboard reports product-level patterns, not actual sales, demand, purchasing frequency, or causal effects. No synthetic data is substituted for the missing workbook.</div>',unsafe_allow_html=True)
    st.stop()

try: data=read_file(raw_bytes,source_name)
except Exception as exc:
    st.error(f"Could not parse the uploaded file: {exc}");st.stop()
if data.empty:st.warning("The source dataset contains no rows.");st.stop()

missing=[c for c in EXPECTED if data[c].isna().all()]
if missing:st.warning("Missing or empty expected fields: "+", ".join(missing)+". Some views may have no data.")

with st.sidebar:
    st.markdown("### Navigation")
    page=st.radio("View",["Executive overview","Brand & category","Pricing & reviews","Product attributes","Data explorer"],label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### Portfolio filters")
    def multi(label,column):
        opts=sorted(data[column].dropna().unique().tolist(),key=str)
        return st.multiselect(label,opts,default=[],placeholder="All",help="Leave empty to include all values.")
    categories=multi("Categories","Category")
    brands=multi("Brands","Brand")
    countries=multi("Origin countries","Country_of_Origin")
    skin=multi("Skin types","Skin_Type")
    cruelty=st.multiselect("Cruelty-free status",["Yes","No","Unknown"],default=[])
    pmin,pmax=data["Price_USD"].min(),data["Price_USD"].max()
    price_range=None
    if pd.notna(pmin) and pd.notna(pmax) and pmax>pmin:
        price_range=st.slider("Price in USD",float(pmin),float(pmax),(float(pmin),float(pmax)),step=round(max((pmax-pmin)/200,.01),2))
    st.markdown("---")
    st.caption(f"Source: {source_name}  ·  {len(data):,} original rows")

mask=pd.Series(True,index=data.index)
for selected,key in [(categories,"Category"),(brands,"Brand"),(countries,"Country_of_Origin"),(skin,"Skin_Type"),(cruelty,"Cruelty_Label")]:
    if selected:mask &= data[key].isin(selected)
if price_range: mask &= data["Price_USD"].between(*price_range)
df=data.loc[mask].copy()

st.markdown('<div class="hero"><div class="eyebrow">STRATEGY & ANALYTICS / BEAUTY SECTOR</div><h1>Beauty Industry Intelligence</h1><p>Executive decision support · Product assortment, competitive positioning and customer feedback indicators. All visuals respond to the active portfolio filters.</p></div>',unsafe_allow_html=True)
if df.empty:st.warning("No products match the selected filters. Adjust the sidebar selections.");st.stop()

n=len(df); rating=df["Rating"].mean(); avgprice=df["Price_USD"].mean(); review=df["Number_of_Reviews"].median()
k1,k2,k3,k4,k5=st.columns(5)
with k1:metric("Products",f"{n:,}",f"{n/len(data):.1%} of full portfolio")
with k2:metric("Brands",f"{df['Brand'].nunique():,}","Distinct brand names")
with k3:metric("Avg. rating",f"{rating:.2f} / 5" if pd.notna(rating) else "—","Product-level mean")
with k4:metric("Avg. price",f"${avgprice:,.2f}" if pd.notna(avgprice) else "—","USD · unweighted")
with k5:metric("Median reviews",f"{review:,.0f}" if pd.notna(review) else "—","Per product")

if page=="Executive overview":
    hdr("Portfolio at a glance","Assortment composition and geographic representation; counts refer to listed products, not units sold.")
    a,b=st.columns([1.15,1])
    with a:
        d=df["Category"].value_counts().head(12).rename_axis("Category").reset_index(name="Products")
        bar(d,"Products","Category","PRODUCT MIX  /  TOP CATEGORIES")
    with b:
        d=df["Country_of_Origin"].value_counts().head(10).rename_axis("Country").reset_index(name="Products")
        bar(d,"Products","Country","GEOGRAPHIC MIX  /  ORIGIN COUNTRIES")
    hdr("Leadership readout")
    top_cat=df["Category"].value_counts(); top_country=df["Country_of_Origin"].value_counts()
    cat_label=top_cat.index[0] if len(top_cat) else "N/A"
    country_label=top_country.index[0] if len(top_country) else "N/A"
    insight(f"<b>{cat_label}</b> leads the filtered assortment with <b>{int(top_cat.iloc[0]):,}</b> product records. <b>{country_label}</b> is the largest listed country of origin with <b>{int(top_country.iloc[0]):,}</b> records. These reflect dataset coverage rather than verified market share or consumer demand.")
    a,b=st.columns(2)
    with a:
        d=df["Gender_Target"].value_counts().rename_axis("Gender target").reset_index(name="Products")
        fig=px.pie(d,names="Gender target",values="Products",hole=.67,color_discrete_sequence=COLORS)
        fig.update_layout(title=dict(text="TARGET SEGMENT MIX",font=dict(size=15)))
        st.plotly_chart(plot_style(fig),use_container_width=True)
    with b:
        d=df["Skin_Type"].value_counts().head(10).rename_axis("Skin type").reset_index(name="Products")
        bar(d,"Products","Skin type","SKIN TYPE COVERAGE")

elif page=="Brand & category":
    hdr("Brand performance","Benchmarks summarize product-level ratings, not brand loyalty or sales performance.")
    minimum=st.slider("Minimum product count per brand",1,max(1,min(100,int(df["Brand"].value_counts().max()))),min(10,max(1,min(100,int(df["Brand"].value_counts().max())))))
    summary=df.groupby("Brand",dropna=False).agg(products=("Product_Name","size"),avg_rating=("Rating","mean"),median_reviews=("Number_of_Reviews","median"),avg_price=("Price_USD","mean")).reset_index()
    eligible=summary[summary["products"]>=minimum]
    a,b=st.columns(2)
    with a:bar(eligible.nlargest(12,"avg_rating").sort_values("avg_rating"),"avg_rating","Brand","TOP BRANDS BY MEAN RATING")
    with b:bar(summary.nlargest(12,"products"),"products","Brand","MOST REPRESENTED BRANDS")
    hdr("Who leads each category?","Winner is the highest average-rated brand within that category. Minimum sample-size rule is applied.")
    ranked=df.groupby(["Category","Brand"],dropna=False).agg(Products=("Rating","size"),Average_Rating=("Rating","mean"),Median_Reviews=("Number_of_Reviews","median")).reset_index()
    ranked=ranked[ranked.Products>=minimum].dropna(subset=["Average_Rating"])
    leaders=ranked.sort_values(["Category","Average_Rating","Products"],ascending=[True,False,False]).drop_duplicates("Category")
    if leaders.empty:st.info("No category/brand combination meets the minimum sample size.")
    else:st.dataframe(leaders.rename(columns={"Category":"Category","Brand":"Leading brand"}).sort_values("Average_Rating",ascending=False),use_container_width=True,hide_index=True)
    insight("<b>Interpretation guardrail:</b> a category leader is a ranking within this dataset, not proof of an industry-leading brand. Brand comparisons are sensitive to product coverage and small sample sizes.")

elif page=="Pricing & reviews":
    hdr("Price architecture & attention proxies","The notebook's price bands are retained: $0–20, $20–50, $50–100 and $100–500.")
    a,b=st.columns(2)
    with a:
        d=df.groupby("Price_Band",dropna=False,observed=True).agg(Products=("Product_Name","size"),Mean_Reviews=("Number_of_Reviews","mean"),Mean_Rating=("Rating","mean")).reset_index()
        order=["Low · $0–20","Mid · $20–50","High · $50–100","Premium · $100–500","Outside bands / unknown"]
        d["Price_Band"]=pd.Categorical(d["Price_Band"],categories=order,ordered=True);d=d.sort_values("Price_Band")
        bar(d,"Price_Band","Mean_Reviews","AVERAGE REVIEWS BY PRICE TIER",orientation="v")
    with b:
        valid=df.dropna(subset=["Price_USD","Rating"])
        fig=px.scatter(valid,x="Price_USD",y="Rating",color="Category",hover_data=["Brand","Product_Name"],opacity=.55,render_mode="webgl",color_discrete_sequence=COLORS)
        fig.update_layout(title=dict(text="PRICE VS. RATING  /  INDIVIDUAL PRODUCTS",font=dict(size=15)))
        st.plotly_chart(plot_style(fig),use_container_width=True)
    a,b=st.columns(2)
    with a:
        d=df.groupby("Category").agg(Mean_Reviews=("Number_of_Reviews","mean")).reset_index().nlargest(12,"Mean_Reviews")
        bar(d,"Mean_Reviews","Category","AVERAGE REVIEWS BY CATEGORY")
    with b:
        valid=df.dropna(subset=["Price_USD"])
        fig=px.box(valid,x="Category",y="Price_USD",color_discrete_sequence=[C["teal"]],points=False)
        fig.update_layout(title=dict(text="PRICE DISPERSION BY CATEGORY",font=dict(size=15)))
        fig.update_xaxes(tickangle=-50)
        st.plotly_chart(plot_style(fig,height=420),use_container_width=True)
    insight("<b>Decision context:</b> price and review count relationships are observational. Review totals are not conversion rates, purchases, revenue, or time-series growth.")

elif page=="Product attributes":
    hdr("Product feature intelligence","Attribute comparisons illuminate assortment structure and descriptive rating differences.")
    a,b=st.columns(2)
    with a:
        d=df.groupby("Cruelty_Label").agg(Products=("Rating","size"),Average_Rating=("Rating","mean")).reset_index()
        bar(d,"Cruelty_Label","Average_Rating","RATING BY CRUELTY-FREE LABEL",orientation="v")
    with b:
        d=df.groupby("Packaging_Type").agg(Products=("Rating","size"),Average_Rating=("Rating","mean")).reset_index().sort_values("Average_Rating",ascending=False)
        bar(d,"Average_Rating","Packaging_Type","RATING BY PACKAGING TYPE")
    a,b=st.columns(2)
    with a:
        d=df["Main_Ingredient"].value_counts().head(12).rename_axis("Ingredient").reset_index(name="Products")
        bar(d,"Products","Ingredient","MOST LISTED MAIN INGREDIENTS")
    with b:
        d=df.groupby("Skin_Type").agg(Products=("Rating","size"),Average_Rating=("Rating","mean")).reset_index().sort_values("Average_Rating",ascending=False)
        bar(d,"Average_Rating","Skin_Type","RATING BY SKIN TYPE")
    hdr("Which ingredient groups have more highly rated products?")
    threshold=st.slider("High-rating threshold",3.0,5.0,4.5,.1)
    temp=df.assign(High_Rated=df["Rating"].ge(threshold).fillna(False))
    ing=temp.groupby("Main_Ingredient").agg(Products=("Product_Name","size"),High_Rated=("High_Rated","sum")).reset_index()
    ing=ing[ing.Products>=10].copy();ing["Share_High_Rated"]=100*ing.High_Rated/ing.Products
    a,b=st.columns(2)
    with a:bar(ing.nlargest(12,"Share_High_Rated"),"Share_High_Rated","Main_Ingredient","% HIGH-RATED WITHIN EACH INGREDIENT")
    with b:
        d=df.groupby("Size_Class").agg(Products=("Rating","size"),Average_Rating=("Rating","mean")).reset_index()
        bar(d,"Size_Class","Average_Rating","AVERAGE RATING / RELATIVE PRODUCT SIZE",orientation="v")
    insight("<b>Interpretation guardrail:</b> ingredient representation and ratings are associations, not evidence that ingredients cause better product outcomes. Size grouping uses the median numeric size extracted from the source, following the notebook; mixed size units can make this comparison unreliable.")

else:
    hdr("Explore the underlying product data","Every table responds to the sidebar filters. Export your current selection for reproducibility.")
    a,b,c=st.columns(3)
    with a:metric("Source rows",f"{len(data):,}","Before active filters")
    with b:metric("Filtered rows",f"{len(df):,}","After active filters")
    with c:metric("Missing ratings",f"{int(df['Rating'].isna().sum()):,}","Filtered subset")
    st.dataframe(df,use_container_width=True,hide_index=True,height=550)
    st.download_button("Download filtered CSV",df.to_csv(index=False).encode("utf-8"),file_name="beauty_intelligence_filtered.csv",mime="text/csv",use_container_width=True)
    with st.expander("Data quality & interpretation notes"):
        st.write(f"Exact duplicate rows in source (after normalization): **{int(data.duplicated(subset=EXPECTED).sum())}**")
        st.write("Missing values (selected numerical columns):")
        st.dataframe(data[["Price_USD","Rating","Number_of_Reviews","Product_Size_Numeric"]].isna().sum().rename("Missing").to_frame())
        st.write("No duplicate rows are dropped automatically. Brand punctuation is preserved. Cruelty-free flags are mapped explicitly to Yes/No/Unknown instead of converting arbitrary strings to Boolean. Price values outside the notebook's fixed tier limits remain visible.")

st.markdown("---")
st.markdown('<div class="micro">BEAUTY INTELLIGENCE  /  RESEARCH DASHBOARD &nbsp; • &nbsp; Product-level exploratory analysis based on the uploaded notebook. All metrics are dynamically calculated from the connected file. They do not establish demand, sales, market share, customer-level behaviour or causality.</div>',unsafe_allow_html=True)
