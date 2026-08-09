"""
Capstone step 2 — EDA with data visualisation.
Produces the six charts needed for slides 18-23, saved as PNG files
so you can drop them straight into the deck.

Input: dataset_part_2.csv (from step 1)
Output: slide18.png ... slide23.png, dataset_part_3.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
DPI = 150

df = pd.read_csv("dataset_part_2.csv")
print(df.head())

# ---------------------------------------------------------------- slide 18
# Flight Number vs. Launch Site
plt.figure(figsize=(11, 6))
sns.catplot(y="LaunchSite", x="FlightNumber", hue="Class", data=df, aspect=2.2)
plt.xlabel("Flight Number", fontsize=14)
plt.ylabel("Launch Site", fontsize=14)
plt.title("Flight Number vs. Launch Site (1 = landed, 0 = failed)")
plt.tight_layout()
plt.savefig("slide18_flightnumber_vs_launchsite.png", dpi=DPI, bbox_inches="tight")
plt.close('all')

# ---------------------------------------------------------------- slide 19
# Payload vs. Launch Site
sns.catplot(y="LaunchSite", x="PayloadMass", hue="Class", data=df, aspect=2.2)
plt.xlabel("Payload Mass (kg)", fontsize=14)
plt.ylabel("Launch Site", fontsize=14)
plt.title("Payload Mass vs. Launch Site")
plt.tight_layout()
plt.savefig("slide19_payload_vs_launchsite.png", dpi=DPI, bbox_inches="tight")
plt.close('all')

# ---------------------------------------------------------------- slide 20
# Success rate by orbit type
orbit_success = df.groupby("Orbit")["Class"].mean().reset_index()
plt.figure(figsize=(11, 5))
sns.barplot(x="Orbit", y="Class", data=orbit_success, color="#1f77b4")
plt.xlabel("Orbit Type", fontsize=13)
plt.ylabel("Success Rate", fontsize=13)
plt.title("Landing Success Rate by Orbit Type")
plt.ylim(0, 1.05)
plt.tight_layout()
plt.savefig("slide20_success_by_orbit.png", dpi=DPI, bbox_inches="tight")
plt.close('all')
print("\nSuccess rate by orbit:\n", orbit_success.sort_values("Class", ascending=False))

# ---------------------------------------------------------------- slide 21
# Flight Number vs. Orbit Type
sns.catplot(y="Orbit", x="FlightNumber", hue="Class", data=df, aspect=2.2)
plt.xlabel("Flight Number", fontsize=14)
plt.ylabel("Orbit Type", fontsize=14)
plt.title("Flight Number vs. Orbit Type")
plt.tight_layout()
plt.savefig("slide21_flightnumber_vs_orbit.png", dpi=DPI, bbox_inches="tight")
plt.close('all')

# ---------------------------------------------------------------- slide 22
# Payload vs. Orbit Type
sns.catplot(y="Orbit", x="PayloadMass", hue="Class", data=df, aspect=2.2)
plt.xlabel("Payload Mass (kg)", fontsize=14)
plt.ylabel("Orbit Type", fontsize=14)
plt.title("Payload Mass vs. Orbit Type")
plt.tight_layout()
plt.savefig("slide22_payload_vs_orbit.png", dpi=DPI, bbox_inches="tight")
plt.close('all')

# ---------------------------------------------------------------- slide 23
# Yearly success trend
def extract_year(dates):
    return [d.split("-")[0] for d in dates]

year_df = df.copy()
year_df["Year"] = extract_year(year_df["Date"].astype(str))
yearly = year_df.groupby("Year")["Class"].mean().reset_index()

plt.figure(figsize=(11, 5))
sns.lineplot(x="Year", y="Class", data=yearly, marker="o")
plt.xlabel("Year", fontsize=13)
plt.ylabel("Average Success Rate", fontsize=13)
plt.title("Launch Success Yearly Trend")
plt.tight_layout()
plt.savefig("slide23_yearly_trend.png", dpi=DPI, bbox_inches="tight")
plt.close('all')
print("\nYearly success rate:\n", yearly)

# ---------------------------------------------------------------- features
features = df[["FlightNumber", "PayloadMass", "Orbit", "LaunchSite", "Flights",
               "GridFins", "Reused", "Legs", "LandingPad", "Block",
               "ReusedCount", "Serial"]]

features_one_hot = pd.get_dummies(
    features,
    columns=["Orbit", "LaunchSite", "LandingPad", "Serial"]
)
features_one_hot = features_one_hot.astype(float)
features_one_hot.to_csv("dataset_part_3.csv", index=False)

print("\nWrote dataset_part_3.csv, shape:", features_one_hot.shape)
print("Charts saved as slide18..slide23 PNG files.")
