"""
Capstone step 1a — SpaceX API collection and data wrangling (slides 8 and 10).

The SpaceX API is intermittently unavailable (HTTP 525 = Cloudflare cannot
reach the origin server). This script retries automatically, and if the API
is still down it falls back to IBM's hosted copy of the same dataset so you
are not blocked.

Produces: dataset_part_1.csv and dataset_part_2.csv
"""

import time
import sys
import requests
import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

BASE = "https://api.spacexdata.com/v4"
FALLBACK = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
            "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")

CUTOFF = pd.Timestamp(2020, 11, 13).date()


def get_json(url, attempts=4, pause=5):
    """GET a URL, retrying on transient server errors."""
    last = None
    for i in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
            # 5xx errors are server-side and worth retrying
            if r.status_code < 500:
                break
        except requests.RequestException as e:
            last = str(e)
        if i < attempts:
            print(f"    attempt {i} failed ({last}), retrying in {pause}s ...")
            time.sleep(pause)
    raise RuntimeError(f"could not fetch {url}: {last}")


# ---------------------------------------------------------------- helpers
def getBoosterVersion(data, out):
    for x in data['rocket']:
        if x:
            out.append(get_json(f"{BASE}/rockets/{x}")['name'])


def getLaunchSite(data, site, lon, lat):
    for x in data['launchpad']:
        if x:
            r = get_json(f"{BASE}/launchpads/{x}")
            lon.append(r['longitude'])
            lat.append(r['latitude'])
            site.append(r['name'])


def getPayloadData(data, mass, orbit):
    for load in data['payloads']:
        if load:
            r = get_json(f"{BASE}/payloads/{load}")
            mass.append(r['mass_kg'])
            orbit.append(r['orbit'])


def getCoreData(data, block, reused, gridfins, reused_count, legs, landing_pad,
                serial, outcome, flights):
    for core in data['cores']:
        if core['core'] is not None:
            r = get_json(f"{BASE}/cores/{core['core']}")
            block.append(r['block'])
            reused_count.append(r['reuse_count'])
            serial.append(r['serial'])
        else:
            block.append(None)
            reused_count.append(None)
            serial.append(None)
        outcome.append(str(core['landing_success']) + ' ' + str(core['landing_type']))
        flights.append(core['flight'])
        gridfins.append(core['gridfins'])
        reused.append(core['reused'])
        legs.append(core['legs'])
        landing_pad.append(core['landpad'])


# ---------------------------------------------------------------- collection
def collect_from_api():
    print("Step 1: requesting past launches from the SpaceX API ...")
    payload = get_json(f"{BASE}/launches/past")
    print("  status code: 200")
    print("  launches returned:", len(payload))

    data = pd.json_normalize(payload)

    print("\nStep 2: reducing to the columns we need ...")
    data = data[['rocket', 'payloads', 'launchpad', 'cores',
                 'flight_number', 'date_utc']]
    data = data[data['cores'].map(len) == 1]
    data = data[data['payloads'].map(len) == 1]
    data['cores'] = data['cores'].map(lambda x: x[0])
    data['payloads'] = data['payloads'].map(lambda x: x[0])
    data['date'] = pd.to_datetime(data['date_utc']).dt.date
    data = data[data['date'] <= CUTOFF]
    print("  rows after filtering:", len(data))

    BoosterVersion, LaunchSite, Longitude, Latitude = [], [], [], []
    PayloadMass, Orbit = [], []
    Block, ReusedCount, Serial = [], [], []
    Outcome, Flights, GridFins, Reused, Legs, LandingPad = [], [], [], [], [], []

    print("\nStep 3: resolving IDs into values (this takes a few minutes) ...")
    print("  rockets ...")
    getBoosterVersion(data, BoosterVersion)
    print("  launchpads ...")
    getLaunchSite(data, LaunchSite, Longitude, Latitude)
    print("  payloads ...")
    getPayloadData(data, PayloadMass, Orbit)
    print("  cores ...")
    getCoreData(data, Block, Reused, GridFins, ReusedCount, Legs, LandingPad,
                Serial, Outcome, Flights)

    print("\nStep 4: building the launch DataFrame ...")
    launch_dict = {
        'FlightNumber': list(data['flight_number']),
        'Date': list(data['date']),
        'BoosterVersion': BoosterVersion,
        'PayloadMass': PayloadMass,
        'Orbit': Orbit,
        'LaunchSite': LaunchSite,
        'Outcome': Outcome,
        'Flights': Flights,
        'GridFins': GridFins,
        'Reused': Reused,
        'Legs': Legs,
        'LandingPad': LandingPad,
        'Block': Block,
        'ReusedCount': ReusedCount,
        'Serial': Serial,
        'Longitude': Longitude,
        'Latitude': Latitude,
    }
    df = pd.DataFrame(launch_dict)
    print("  shape:", df.shape)

    print("\nStep 5: filtering to Falcon 9 and resetting flight number ...")
    f9 = df[df['BoosterVersion'] != 'Falcon 1'].copy()
    f9.loc[:, 'FlightNumber'] = list(range(1, f9.shape[0] + 1))
    print("  Falcon 9 launches:", len(f9))

    print("\nStep 6: imputing missing payload mass with the column mean ...")
    mean_mass = f9['PayloadMass'].mean()
    print("  mean payload mass:", round(mean_mass, 2))
    f9['PayloadMass'] = f9['PayloadMass'].replace(np.nan, mean_mass)
    print("  missing values remaining:")
    print(f9.isnull().sum())

    f9.to_csv('dataset_part_1.csv', index=False)
    print("\n  wrote dataset_part_1.csv")
    return f9


def wrangle(df):
    print("\n" + "=" * 70)
    print("DATA WRANGLING  (slide 10)")
    print("=" * 70)

    print("\nLaunches per site:")
    print(df['LaunchSite'].value_counts())

    print("\nOccurrence of each orbit:")
    print(df['Orbit'].value_counts())

    landing_outcomes = df['Outcome'].value_counts()
    print("\nLanding outcomes:")
    print(landing_outcomes)

    print("\nOutcomes indexed:")
    for i, outcome in enumerate(landing_outcomes.keys()):
        print(" ", i, outcome)

    bad_outcomes = set(landing_outcomes.keys()[[1, 3, 5, 6, 7]])
    print("\nUnsuccessful outcomes:", bad_outcomes)

    df['Class'] = [0 if o in bad_outcomes else 1 for o in df['Outcome']]

    print("\nClass column (first 8):", list(df['Class'].values[:8]))
    print("Overall success rate:", round(df['Class'].mean(), 4))

    df.to_csv("dataset_part_2.csv", index=False)
    print("\n  wrote dataset_part_2.csv")
    return df


if __name__ == "__main__":
    try:
        api_df = collect_from_api()
        wrangle(api_df)
        print("\nDone. Screenshot the output above for slides 8 and 10.")
    except RuntimeError as e:
        print("\n" + "!" * 70)
        print("The SpaceX API is unavailable:", e)
        print("!" * 70)
        print("\nHTTP 525 means Cloudflare cannot reach the SpaceX origin server.")
        print("This is an outage on their side, not a problem with your setup.")
        print("\nFalling back to IBM's hosted copy of the same dataset so that")
        print("you can continue with the EDA charts (slides 18-23).")
        print("Re-run this script later to produce slides 8 and 10 properly.\n")
        try:
            df = pd.read_csv(FALLBACK)
            df.to_csv("dataset_part_2.csv", index=False)
            print("  wrote dataset_part_2.csv from the IBM fallback")
            print("  shape:", df.shape)
            print("\nYou can now run: python 02_eda_visualization.py")
        except Exception as e2:
            print("  the fallback also failed:", e2)
            sys.exit(1)
