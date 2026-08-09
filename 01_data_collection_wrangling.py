"""
Capstone step 1 — data collection (SpaceX API + web scraping) and data wrangling.
Produces: dataset_part_1.csv, spacex_web_scraped.csv, dataset_part_2.csv

Screenshots for slides 8, 9, 10 come from the printed output of this script.
"""

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# ----------------------------------------------------------------------
# PART A — SpaceX REST API  (slide 8)
# ----------------------------------------------------------------------

BASE = "https://api.spacexdata.com/v4"

# Helper functions: the API returns IDs, so each one is resolved to a value.
def getBoosterVersion(data, out):
    for x in data['rocket']:
        if x:
            r = requests.get(f"{BASE}/rockets/{x}").json()
            out.append(r['name'])

def getLaunchSite(data, site, lon, lat):
    for x in data['launchpad']:
        if x:
            r = requests.get(f"{BASE}/launchpads/{x}").json()
            lon.append(r['longitude'])
            lat.append(r['latitude'])
            site.append(r['name'])

def getPayloadData(data, mass, orbit):
    for load in data['payloads']:
        if load:
            r = requests.get(f"{BASE}/payloads/{load}").json()
            mass.append(r['mass_kg'])
            orbit.append(r['orbit'])

def getCoreData(data, block, reused, gridfins, reused_count, legs, landing_pad,
                serial, outcome, flights):
    for core in data['cores']:
        if core['core'] is not None:
            r = requests.get(f"{BASE}/cores/{core['core']}").json()
            block.append(r['block'])
            reused_count.append(r['reuse_count'])
            serial.append(r['serial'])
        else:
            block.append(None); reused_count.append(None); serial.append(None)
        outcome.append(str(core['landing_success']) + ' ' + str(core['landing_type']))
        flights.append(core['flight'])
        gridfins.append(core['gridfins'])
        reused.append(core['reused'])
        legs.append(core['legs'])
        landing_pad.append(core['landpad'])


def collect_from_api():
    print("Requesting past launches from the SpaceX API ...")
    resp = requests.get(f"{BASE}/launches/past")
    print("  status code:", resp.status_code)

    data = pd.json_normalize(resp.json())

    # Keep only the columns needed, then drop multi-payload / multi-core rows
    data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
    data = data[data['cores'].map(len) == 1]
    data = data[data['payloads'].map(len) == 1]
    data['cores'] = data['cores'].map(lambda x: x[0])
    data['payloads'] = data['payloads'].map(lambda x: x[0])
    data['date'] = pd.to_datetime(data['date_utc']).dt.date
    data = data[data['date'] <= pd.datetime(2020, 11, 13).date()] if hasattr(pd, 'datetime') \
        else data[data['date'] <= pd.Timestamp(2020, 11, 13).date()]

    BoosterVersion, LaunchSite, Longitude, Latitude = [], [], [], []
    PayloadMass, Orbit = [], []
    Block, ReusedCount, Serial = [], [], []
    Outcome, Flights, GridFins, Reused, Legs, LandingPad = [], [], [], [], [], []

    print("Resolving booster, launchpad, payload and core IDs ...")
    getBoosterVersion(data, BoosterVersion)
    getLaunchSite(data, LaunchSite, Longitude, Latitude)
    getPayloadData(data, PayloadMass, Orbit)
    getCoreData(data, Block, Reused, GridFins, ReusedCount, Legs, LandingPad,
                Serial, Outcome, Flights)

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

    # Filter to Falcon 9 only and reset the flight number
    data_falcon9 = df[df['BoosterVersion'] != 'Falcon 1'].copy()
    data_falcon9.loc[:, 'FlightNumber'] = list(range(1, data_falcon9.shape[0] + 1))

    # Impute missing payload mass with the column mean
    mean_mass = data_falcon9['PayloadMass'].mean()
    print("  mean payload mass used for imputation:", round(mean_mass, 2))
    data_falcon9['PayloadMass'] = data_falcon9['PayloadMass'].replace(np.nan, mean_mass)

    print("  missing values after imputation:")
    print(data_falcon9.isnull().sum())

    data_falcon9.to_csv('dataset_part_1.csv', index=False)
    print("  -> wrote dataset_part_1.csv, shape:", data_falcon9.shape)
    return data_falcon9


# ----------------------------------------------------------------------
# PART B — Web scraping Wikipedia  (slide 9)
# ----------------------------------------------------------------------

STATIC_URL = ("https://en.wikipedia.org/w/index.php?title="
              "List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922")

HEADERS = {
    "User-Agent": "SpaceXCapstoneCoursework/1.0 (student project; contact: your-email@example.com)"
}


def date_time(table_cells):
    return [dt.strip() for dt in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    return ''.join([b for i, b in enumerate(table_cells.strings) if i % 2 == 0][0:-1])

def landing_status(table_cells):
    return [i for i in table_cells.strings][0]

def get_mass(table_cells):
    mass = table_cells.text.strip()
    if mass:
        idx = mass.find("kg")
        return mass[0:idx + 2]
    return None

def extract_column_from_header(row):
    for br in row.find_all("br"):
        br.extract()
    for a in row.find_all("a"):
        a.extract()
    for st in row.find_all("sup"):
        st.extract()
    name = ' '.join(row.contents).strip()
    if name and not name.isdigit():
        return name
    return None


def collect_from_wikipedia():
    print("\nRequesting the Wikipedia launch records page ...")
    resp = requests.get(STATIC_URL, headers=HEADERS, timeout=30)
    print("  status code:", resp.status_code)

    soup = BeautifulSoup(resp.text, 'html.parser')
    print("  page title:", soup.title.string)

    tables = soup.find_all('table', "wikitable plainrowheaders collapsible")
    first_table = tables[2]

    column_names = []
    for th in first_table.find_all('th'):
        name = extract_column_from_header(th)
        if name is not None and len(name) > 0:
            column_names.append(name)
    print("  column names found:", column_names)

    launch_dict = dict.fromkeys(column_names)
    for k in ['Date and time ( )', 'Launch outcome']:
        launch_dict.pop(k, None)
    for k in list(launch_dict.keys()):
        launch_dict[k] = []
    launch_dict['Version Booster'] = []
    launch_dict['Booster landing'] = []
    launch_dict['Date'] = []
    launch_dict['Time'] = []

    extracted_row = 0
    for table_number, table in enumerate(
            soup.find_all('table', "wikitable plainrowheaders collapsible")):
        for rows in table.find_all("tr"):
            if rows.th and rows.th.string:
                flight_number = rows.th.string.strip()
                flag = flight_number.isdigit()
            else:
                flag = False

            row = rows.find_all('td')
            if not flag:
                continue

            extracted_row += 1
            launch_dict['Flight No.'].append(flight_number)

            datatimelist = date_time(row[0])
            launch_dict['Date'].append(datatimelist[0].strip(','))
            launch_dict['Time'].append(datatimelist[1])

            launch_dict['Version Booster'].append(booster_version(row[1])
                                                  or row[1].a.string)
            launch_dict['Launch site'].append(row[2].a.string)
            launch_dict['Payload'].append(row[3].a.string)
            launch_dict['Payload mass'].append(get_mass(row[4]))
            launch_dict['Orbit'].append(row[5].a.string)
            launch_dict['Customer'].append(
                row[6].a.string if row[6].a else row[6].get_text(strip=True))
            launch_dict['Launch outcome'] = launch_dict.get('Launch outcome', [])
            launch_dict['Booster landing'].append(landing_status(row[8]))

    df = pd.DataFrame({k: pd.Series(v) for k, v in launch_dict.items()})
    df.to_csv('spacex_web_scraped.csv', index=False)
    print("  -> wrote spacex_web_scraped.csv, rows extracted:", extracted_row)
    return df


# ----------------------------------------------------------------------
# PART C — Data wrangling  (slide 10)
# ----------------------------------------------------------------------

def wrangle(df):
    print("\n--- Data wrangling ---")

    print("\nLaunches per site:")
    print(df['LaunchSite'].value_counts())

    print("\nOccurrence of each orbit:")
    print(df['Orbit'].value_counts())

    landing_outcomes = df['Outcome'].value_counts()
    print("\nLanding outcomes:")
    print(landing_outcomes)

    for i, outcome in enumerate(landing_outcomes.keys()):
        print(i, outcome)

    # Outcomes that represent an unsuccessful landing
    bad_outcomes = set(landing_outcomes.keys()[[1, 3, 5, 6, 7]])
    print("\nUnsuccessful outcomes:", bad_outcomes)

    landing_class = [0 if outcome in bad_outcomes else 1 for outcome in df['Outcome']]
    df['Class'] = landing_class

    print("\nClass column (first 8):", df['Class'].values[:8])
    print("Overall success rate:", round(df['Class'].mean(), 4))

    df.to_csv("dataset_part_2.csv", index=False)
    print("  -> wrote dataset_part_2.csv")
    return df


if __name__ == "__main__":
    api_df = collect_from_api()
    collect_from_wikipedia()
    wrangle(api_df)
    print("\nDone. Screenshot the printed output above for slides 8, 9 and 10.")
