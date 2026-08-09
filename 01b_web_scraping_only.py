"""
Capstone step 1b — web scraping only (slide 9).
Runs independently of the SpaceX API, so it works even while api.spacexdata.com
is down. Produces spacex_web_scraped.csv.

Screenshot the printed output for slide 9.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# Pinned to a fixed revision so the table structure does not shift underneath us
STATIC_URL = ("https://en.wikipedia.org/w/index.php?title="
              "List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922")

# Wikipedia returns 403 to the default requests user-agent. Their policy asks
# for a descriptive one identifying the tool and a contact.
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


print("Step 1: requesting the Wikipedia launch records page ...")
resp = requests.get(STATIC_URL, headers=HEADERS, timeout=30)
print("  status code:", resp.status_code)
resp.raise_for_status()

print("\nStep 2: creating the BeautifulSoup object ...")
soup = BeautifulSoup(resp.text, 'html.parser')
print("  page title:", soup.title.string)

print("\nStep 3: locating the launch tables ...")
html_tables = soup.find_all('table', "wikitable plainrowheaders collapsible")
print("  tables found:", len(html_tables))
first_launch_table = html_tables[2]

print("\nStep 4: extracting column names from the table header ...")
column_names = []
for th in first_launch_table.find_all('th'):
    name = extract_column_from_header(th)
    if name is not None and len(name) > 0:
        column_names.append(name)
print("  column names:", column_names)

print("\nStep 5: parsing every launch row ...")
launch_dict = dict.fromkeys(column_names)
for key in ['Date and time ( )', 'Launch outcome']:
    launch_dict.pop(key, None)
for key in list(launch_dict.keys()):
    launch_dict[key] = []
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

        bv = booster_version(row[1])
        if not bv:
            bv = row[1].a.string if row[1].a else None
        launch_dict['Version Booster'].append(bv)

        launch_dict['Launch site'].append(
            row[2].a.string if row[2].a else row[2].get_text(strip=True))
        launch_dict['Payload'].append(
            row[3].a.string if row[3].a else row[3].get_text(strip=True))
        launch_dict['Payload mass'].append(get_mass(row[4]))
        launch_dict['Orbit'].append(
            row[5].a.string if row[5].a else row[5].get_text(strip=True))
        launch_dict['Customer'].append(
            row[6].a.string if row[6].a else row[6].get_text(strip=True))
        launch_dict['Booster landing'].append(landing_status(row[8]))

print("  rows extracted:", extracted_row)

df = pd.DataFrame({key: pd.Series(value) for key, value in launch_dict.items()})
df.to_csv('spacex_web_scraped.csv', index=False)

print("\nStep 6: resulting DataFrame")
print("  shape:", df.shape)
print(df.head())

print("\nWrote spacex_web_scraped.csv")
print("Screenshot the output above for slide 9.")
