import sqlite3
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def update_row_coords(db,locator,row):
    cur = db.cursor()

    geo = locator.geocode(f"{row[1]} {row[2]} {row[3]}")
    geo = locator.geocode(f"{row[1]} {row[3]}") if geo == None else geo
    geo = locator.geocode(f"{row[2]} {row[3]}") if geo == None else geo
    geo = locator.geocode(f"{row[3]}") if geo == None else geo

    cur.execute("UPDATE geo SET latitude = ?, longitude = ? where code_bassin = ?",(geo.latitude,geo.longitude,row[0]))

db = sqlite3.connect("Emploi.db")

locator = Nominatim(user_agent="myGeocoder",timeout=10) # type: ignore
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)

cur = db.cursor()
# cur.execute("ALTER TABLE geo ADD latitude REAL")
# cur.execute("ALTER TABLE geo ADD longitude REAL")

cur.execute("SELECT code_bassin, nom_bassin,nom_dept,nom_reg FROM geo")

rows=cur.fetchall()
i=0
for row in rows:
    i+=1
    update_row_coords(db,locator,row)

    if i%20==0:
        print(f"{int((i*100)/len(rows))}%   ------------------------------  ligne {i} (sur {len(rows)})")

db.commit()
db.close()
