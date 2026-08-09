# SpaceX Capstone — code for every missing screenshot

Run these in order. Each one prints or saves exactly what a slide needs.

## Setup

```bash
pip install pandas numpy requests beautifulsoup4 matplotlib seaborn \
            folium plotly dash scikit-learn
```

## Run order

| Script | Produces | Slides |
|---|---|---|
| `01_data_collection_wrangling.py` | printed output, `dataset_part_1.csv`, `spacex_web_scraped.csv`, `dataset_part_2.csv` | 8, 9, 10 |
| `02_eda_visualization.py` | `slide18..slide23` PNGs, `dataset_part_3.csv` | 18–23 |
| `03_eda_sql.py` | ten printed query blocks | 24–33 |
| `04_folium_map.py` | three HTML maps | 35–37 |
| `05_dash_app.py` | live dashboard at `http://127.0.0.1:8050` | 39–41 |
| `06_predictive_analysis.py` | two PNGs + printed scores | 43, 44 |

Scripts 3–6 pull data directly from IBM's hosted CSVs, so they run
independently of script 1. Script 2 needs script 1 to have run first.

## Screenshot checklist

- [ ] 8 — API collection output (also draw a flowchart for the right-hand box)
- [ ] 9 — scraping output (also draw a flowchart)
- [ ] 10 — wrangling output: value counts and the Class column
- [ ] 18 — Flight Number vs. Launch Site
- [ ] 19 — Payload vs. Launch Site
- [ ] 20 — Success rate by orbit
- [ ] 21 — Flight Number vs. Orbit
- [ ] 22 — Payload vs. Orbit
- [ ] 23 — Yearly success trend
- [ ] 24–33 — one screenshot per query, showing the SQL *and* its result
- [ ] 35 — all launch site markers, zoomed to show both coasts
- [ ] 36 — colour-coded outcome clusters (expand a cluster before shooting)
- [ ] 37 — proximity lines with distance labels
- [ ] 39 — pie chart, "All Sites"
- [ ] 40 — pie chart, single site with the best ratio
- [ ] 41 — scatter at two or three slider ranges
- [ ] 43 — accuracy bar chart
- [ ] 44 — confusion matrix

## Two things to double-check

**Slide 37 coordinates.** The four points of interest are hard-coded for
CCAFS SLC-40. The map includes a MousePosition readout — hover over the
actual coastline, railway and highway near your chosen site and replace the
coordinates in `points` with what you read off.

**Slide 43–44 numbers.** The deck currently claims all four models reach
83.3% and that the decision tree wins on cross-validation. Run script 6 and
use whatever it actually prints. The test set has only 18 rows, so the
ranking can shift with a different `random_state`.

**Dataset URLs.** If any script fails with `HTTP Error 404`, the IBM path has
moved. Open the failing lab on Coursera, copy the URL from its `pd.read_csv`
line, and paste it into the script. Only the SQL dataset lives under
`/labs/module_2/data/`; everything else (`spacex_launch_geo.csv`,
`spacex_launch_dash.csv`, `dataset_part_2.csv`, `dataset_part_3.csv`) lives
under `/datasets/`.

**Wikipedia 403 Forbidden.** Wikipedia rejects the default `requests`
user-agent. The scraping scripts set a descriptive `User-Agent` header, as
their policy requires — edit the contact address in it to your own.

**SpaceX API HTTP 525.** Cloudflare cannot reach SpaceX's origin server;
this is an outage on their side and usually clears within a few hours.
`01a_api_collection.py` retries automatically and falls back to IBM's hosted
copy of `dataset_part_2.csv` so the EDA charts are not blocked.

**scikit-learn version.** On very recent scikit-learn (1.8+), the
`penalty='l2'` entry in the logistic-regression grid raises a
`FutureWarning`. It still runs. If your version errors instead of warning,
drop `'penalty'` from `parameters_lr` and keep only `C` and `solver`. The
Coursera lab environment uses an older version where the original grid is
fine.

## Note on the notebooks

The graded labs walk through this same code with explanations, and the peer
review asks you to describe your own process. Treat these scripts as a
reference to check your work against rather than a substitute for the labs —
you'll be asked to explain the methodology slides, and it's much easier when
you've stepped through it yourself.
