"""
Capstone step 4 — Interactive map with Folium.
Produces three HTML maps for slides 35, 36 and 37. Open each in a browser,
zoom to a sensible level, and screenshot.

Output: map1_sites.html, map2_outcomes.html, map3_proximities.html
"""

import folium
import pandas as pd
from math import sin, cos, sqrt, atan2, radians
from folium.plugins import MarkerCluster, MousePosition
from folium.features import DivIcon

URL = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv")

spacex_df = pd.read_csv(URL)

# One row per launch site with its coordinates
spacex_df = spacex_df[['Launch Site', 'Lat', 'Long', 'class']]
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site', 'Lat', 'Long']]
print(launch_sites_df)

NASA_COORD = [29.559684888503615, -95.0830971930759]


# ------------------------------------------------------------ MAP 1 (slide 35)
site_map = folium.Map(location=NASA_COORD, zoom_start=5)

for _, row in launch_sites_df.iterrows():
    coordinate = [row['Lat'], row['Long']]
    folium.Circle(
        coordinate, radius=1000, color='#d35400', fill=True
    ).add_child(folium.Popup(row['Launch Site'])).add_to(site_map)
    folium.map.Marker(
        coordinate,
        icon=DivIcon(
            icon_size=(20, 20),
            icon_anchor=(0, 0),
            html='<div style="font-size:12px; color:#d35400;"><b>%s</b></div>'
                 % row['Launch Site'],
        )
    ).add_to(site_map)

site_map.save("map1_sites.html")
print("wrote map1_sites.html  -> screenshot for slide 35")


# ------------------------------------------------------------ MAP 2 (slide 36)
site_map2 = folium.Map(location=NASA_COORD, zoom_start=5)
marker_cluster = MarkerCluster()

def assign_marker_color(launch_outcome):
    return 'green' if launch_outcome == 1 else 'red'

spacex_df['marker_color'] = spacex_df['class'].apply(assign_marker_color)
site_map2.add_child(marker_cluster)

for _, record in spacex_df.iterrows():
    folium.Marker(
        location=[record['Lat'], record['Long']],
        icon=folium.Icon(color='white', icon_color=record['marker_color']),
        popup=f"{record['Launch Site']} — {'Success' if record['class'] == 1 else 'Failure'}"
    ).add_to(marker_cluster)

site_map2.save("map2_outcomes.html")
print("wrote map2_outcomes.html -> screenshot for slide 36")

# Success rate per site, useful for the slide explanation
print("\nSuccess rate by site:")
print(spacex_df.groupby('Launch Site')['class'].mean().sort_values(ascending=False))


# ------------------------------------------------------------ MAP 3 (slide 37)
def calculate_distance(lat1, lon1, lat2, lon2):
    """Great-circle distance in km (Haversine)."""
    R = 6373.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * (2 * atan2(sqrt(a), sqrt(1 - a)))


site_map3 = folium.Map(location=[28.56321, -80.57683], zoom_start=13)
MousePosition(
    position='topright', separator=' Long: ', empty_string='NaN',
    lng_first=False, num_digits=20, prefix='Lat:'
).add_to(site_map3)

# CCAFS SLC-40 and four nearby points of interest.
# Use the MousePosition readout to replace these with your own coordinates.
launch_site = (28.56321, -80.57683)
points = {
    'Coastline':  (28.56367, -80.56789),
    'Railway':    (28.57209, -80.58527),
    'Highway':    (28.56335, -80.57076),
    'Titusville': (28.61208, -80.80764),
}

folium.Marker(
    launch_site,
    icon=DivIcon(icon_size=(20, 20), icon_anchor=(0, 0),
                 html='<div style="font-size:12px;"><b>CCAFS SLC-40</b></div>')
).add_to(site_map3)

for name, coord in points.items():
    distance = calculate_distance(launch_site[0], launch_site[1], coord[0], coord[1])
    folium.Marker(
        coord,
        icon=DivIcon(
            icon_size=(20, 20), icon_anchor=(0, 0),
            html='<div style="font-size:12px; color:#d35400;"><b>%s: %.2f KM</b></div>'
                 % (name, distance))
    ).add_to(site_map3)
    folium.PolyLine([launch_site, coord], weight=1, color='blue').add_to(site_map3)
    print(f"Distance to {name}: {distance:.2f} km")

site_map3.save("map3_proximities.html")
print("wrote map3_proximities.html -> screenshot for slide 37")
