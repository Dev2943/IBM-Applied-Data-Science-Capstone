"""
Capstone step 3 — EDA with SQL.
Runs the ten queries needed for slides 24-33 against a SQLite database
and prints each query with its result, ready to screenshot.

In the Coursera lab this uses IBM Db2 with %sql magic. SQLite is used here
so it runs anywhere; the SQL itself is the same.
"""

import sqlite3
import pandas as pd

CSV = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
       "IBM-DS0321EN-SkillsNetwork/labs/module_2/data/Spacex.csv")

con = sqlite3.connect("my_data1.db")
df = pd.read_csv(CSV)
df.to_sql("SPACEXTBL", con, if_exists="replace", index=False, method="multi")

# The lab creates a cleaned table with no blank rows
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS SPACEXTABLE;")
cur.execute("CREATE TABLE SPACEXTABLE AS "
            "SELECT * FROM SPACEXTBL WHERE Date IS NOT NULL;")
con.commit()

TABLE = "SPACEXTABLE"

QUERIES = [
    ("Slide 24 — All launch site names",
     f"SELECT DISTINCT Launch_Site FROM {TABLE};"),

    ("Slide 25 — Launch sites beginning with 'CCA'",
     f"SELECT * FROM {TABLE} WHERE Launch_Site LIKE 'CCA%' LIMIT 5;"),

    ("Slide 26 — Total payload mass carried by NASA (CRS) boosters",
     f"SELECT SUM(PAYLOAD_MASS__KG_) AS Total_Payload_Mass "
     f"FROM {TABLE} WHERE Customer = 'NASA (CRS)';"),

    ("Slide 27 — Average payload mass for booster version F9 v1.1",
     f"SELECT AVG(PAYLOAD_MASS__KG_) AS Average_Payload_Mass "
     f"FROM {TABLE} WHERE Booster_Version = 'F9 v1.1';"),

    ("Slide 28 — Date of the first successful ground pad landing",
     f"SELECT MIN(Date) AS First_Successful_Ground_Landing "
     f"FROM {TABLE} WHERE Landing_Outcome = 'Success (ground pad)';"),

    ("Slide 29 — Boosters: drone ship success, payload 4000-6000 kg",
     f"SELECT DISTINCT Booster_Version FROM {TABLE} "
     f"WHERE Landing_Outcome = 'Success (drone ship)' "
     f"AND PAYLOAD_MASS__KG_ > 4000 AND PAYLOAD_MASS__KG_ < 6000;"),

    ("Slide 30 — Total successful and failed mission outcomes",
     f"SELECT Mission_Outcome, COUNT(*) AS Total "
     f"FROM {TABLE} GROUP BY Mission_Outcome;"),

    ("Slide 31 — Boosters that carried the maximum payload mass",
     f"SELECT DISTINCT Booster_Version FROM {TABLE} "
     f"WHERE PAYLOAD_MASS__KG_ = (SELECT MAX(PAYLOAD_MASS__KG_) FROM {TABLE});"),

    ("Slide 32 — 2015 failed drone ship landings, by month",
     f"SELECT substr(Date, 6, 2) AS Month, Landing_Outcome, "
     f"Booster_Version, Launch_Site FROM {TABLE} "
     f"WHERE substr(Date, 1, 4) = '2015' "
     f"AND Landing_Outcome = 'Failure (drone ship)';"),

    ("Slide 33 — Landing outcomes ranked, 2010-06-04 to 2017-03-20",
     f"SELECT Landing_Outcome, COUNT(*) AS Outcome_Count FROM {TABLE} "
     f"WHERE Date BETWEEN '2010-06-04' AND '2017-03-20' "
     f"GROUP BY Landing_Outcome ORDER BY Outcome_Count DESC;"),
]

for title, sql in QUERIES:
    print("\n" + "=" * 78)
    print(title)
    print("-" * 78)
    print(sql)
    print("-" * 78)
    try:
        print(pd.read_sql_query(sql, con).to_string(index=False))
    except Exception as e:
        print("ERROR:", e)

con.close()
print("\n\nScreenshot each query block above for its matching slide.")
