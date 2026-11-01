# Beauty Intelligence — Boardroom Dashboard

An executive-style Streamlit dashboard based on the supplied *Demystifying the Beauty Industry* analysis notebook. Dark navy, champagne-gold accents, dynamic filters, polished Plotly visualizations, and a dedicated data-explorer tab.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Upload the **original `project.xlsx`** through the sidebar, or place it next to `app.py`. CSV files with the same columns are supported.

**Important:** The shared `.ipynb` references `project.xlsx` but doesn't include the full 15,000-row workbook. The app never invents or generates records. Until you connect that data, it shows a polished upload/overview screen.

## Sections

1. Executive overview: KPIs, category mix, country-of-origin distribution, gender-target and skin-type coverage, and a dynamically generated leadership note.
2. Brand & category: brand scorecards with configurable sample-size threshold, average rating rankings, category leaders, product counts.
3. Pricing & reviews: original fixed price tiers, mean reviews, price/rating scatterplot, category review counts and price distributions.
4. Product attributes: cruelty-free comparison, packaging, ingredients, skin types, size classes and within-ingredient high-rating shares.
5. Data explorer: responsive table, QA checks, export filtered results to CSV.

Filters: categories, brands, origin countries, skin types, cruelty-free classification, and price range.

## Source fidelity and analytical safeguards

- The source contains **14 columns**: Product_Name, Brand, Category, Usage_Frequency, Price_USD, Rating, Number_of_Reviews, Product_Size, Skin_Type, Gender_Target, Packaging_Type, Main_Ingredient, Cruelty_Free and Country_of_Origin.
- Product *counts* are deliberately not described as consumers or sales. Reviews are an engagement **proxy**, not revenue.
- `pd.cut` uses the notebook's boundaries of 0, 20, 50, 100, 500 dollars; outside-range products are retained.
- Brand punctuation is preserved; arbitrary text isn't coerced into True for cruelty-free flags.
- High-rated ingredient percentages use each ingredient's total product count as denominator, improving on the notebook's raw top-rated counts.
- Rankings by mean rating should be interpreted cautiously because of sample sizes and rating variation.
- Product size units are not harmonized if the underlying dataset includes mixed measurements; relative size analysis must be treated with caution.
- No sales, temporal trends, causal effects, or statistically significant differences are claimed.

## Deployment

For Streamlit Community Cloud, place `app.py`, `requirements.txt`, and `.streamlit/config.toml` in a GitHub repository. Deploy the repo and upload your Excel through the application (or add the dataset to your repo if you're permitted to publish it). Never publish a confidential dataset.
