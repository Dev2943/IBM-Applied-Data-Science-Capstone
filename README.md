# Winning the Space Race with Data Science

IBM Applied Data Science Capstone. The goal is to predict whether the first
stage of a SpaceX Falcon 9 will land successfully after launch.

This matters commercially: SpaceX advertises Falcon 9 launches at around
$62 million where other providers charge upward of $165 million, and the
difference comes from recovering and reusing the first stage. A launch where
the booster is lost costs substantially more than one where it is recovered,
so predicting the landing outcome is effectively predicting the true cost of
a launch — useful to anyone bidding against SpaceX for a contract.

## Data

90 Falcon 9 launches, from the first flight in 2010 through November 2020,
assembled from two independent sources:

- **SpaceX REST API v4** (`/launches/past`) — the nested JSON is flattened,
  and follow-up calls resolve booster, launchpad, payload and core IDs into
  readable values.
- **Wikipedia**, *List of Falcon 9 and Falcon Heavy launches* — the launch
  records table is scraped with BeautifulSoup, pinned to a fixed revision so
  the table structure does not shift.

Missing payload masses are imputed with the column mean. The target column
`Class` is 1 where the booster landed and 0 otherwise, derived by treating
False ASDS, False RTLS, False Ocean, None ASDS and None None as failures.
Two thirds of launches in the dataset (66.7%) ended in a successful landing.

## Findings

**Success improved sharply over time.** No recovery was attempted before
2013, so the early zeros reflect the absence of an attempt rather than
failure. The rate climbs from 33.3% in 2014 to 83.3% in 2017, dips to 61.1%
in 2018, then peaks at 90.0% in 2019 and holds at 84.2% in 2020. Flight
number is therefore a strong predictor, essentially standing in for accrued
experience and booster maturity.

**Launch site matters, but is confounded with time.** KSC LC-39A lands 77.3%
of its 22 launches and VAFB SLC-4E 76.9% of its 13, against 60.0% for CCAFS
SLC-40 across 55 launches. CCAFS carries most of the early flights, so part
of its lower rate is the era it flew in rather than the pad itself.

Note that `SELECT DISTINCT Launch_Site` returns four values, not three:
Cape Canaveral's LC-40 was redesignated SLC-40 partway through the record,
so the same physical pad appears under both names.

**Orbit is strongly associated with outcome, but the extremes are thin.**
ES-L1, GEO, HEO and SSO show 100% success and SO shows 0% — each on only one
or two launches, so these are not meaningful rates. The substantive finding
is GTO at 51.9% across 27 launches, making it the least predictable orbit in
the dataset.

**Payload has a threshold effect at some sites.** At KSC LC-39A every launch
below 5,300 kg landed, and all three failures occurred above 5,600 kg,
suggesting a boundary near 5,500 kg. Across all sites, though, payload alone
does not explain GTO outcomes.

**All four classifiers reach 83.3% test accuracy.** Logistic regression, SVM,
decision tree and KNN were tuned with `GridSearchCV` at 10-fold CV and
evaluated on the same held-out split. The decision tree led on
cross-validated training accuracy (87.7%) but the tie on the test set is an
artefact of size: the test set has only 18 rows, so one row is worth 5.6
percentage points and the models cannot be separated at this resolution.

The confusion matrix is more informative than the accuracy. Recall is 1.00
on the landed class but 0.50 on the failure class — every error is a false
positive, a booster predicted to land that did not. For the cost-estimation
use case this is the expensive direction to be wrong in, since it
systematically underestimates the price of a launch. Accuracy alone
overstates how useful the model is.

## Repository contents

| File | What it does |
|---|---|
| `01a_api_collection.py` | SpaceX API collection and wrangling; writes `dataset_part_1.csv`, `dataset_part_2.csv` |
| `01b_web_scraping_only.py` | Wikipedia scraping; writes `spacex_web_scraped.csv` |
| `01_data_collection_wrangling.py` | Both collection paths and the wrangling step in one script |
| `02_eda_visualization.py` | Six EDA charts; writes `dataset_part_3.csv` (90 × 80 after one-hot encoding) |
| `03_eda_sql.py` | Ten SQL queries against a SQLite copy of the launch table |
| `04_folium_map.py` | Three interactive maps: sites, outcome clusters, proximity lines |
| `05_dash_app.py` | Plotly Dash dashboard with a site dropdown and payload slider |
| `06_predictive_analysis.py` | Trains, tunes and evaluates the four classifiers |

## Running it

```bash
pip install pandas numpy requests beautifulsoup4 matplotlib seaborn \
            folium plotly dash scikit-learn
```

Scripts 3–6 read IBM's hosted copies of the datasets, so they run
independently. Script 2 needs script 1 to have run first. The Dash app
serves at `http://127.0.0.1:8050`.

Two environment notes: Wikipedia rejects the default `requests` user-agent,
so the scraping scripts send a descriptive one — edit the contact address to
your own. The SpaceX API intermittently returns HTTP 525 when Cloudflare
cannot reach its origin; `01a_api_collection.py` retries and falls back to
IBM's hosted copy of the same dataset.

## Methods

pandas and NumPy for wrangling, Matplotlib and Seaborn for the charts,
BeautifulSoup for scraping, SQLite for the SQL analysis, Folium for the
maps, Plotly Dash for the dashboard, and scikit-learn for the models.
Features are standardised with `StandardScaler` before an 80/20 split with a
fixed random state.
