---
name: folium-interactive-map-creation
description: 'Folium patterns: Map+Marker creation, lat/lon extraction from dicts, seeded coordinate generation per city, mixed input handling, and geodesic distance computation.'
---

# Folium — Interactive Map Creation

Folium creates Leaflet.js maps in Python. Core pattern: create `folium.Map`, add `folium.Marker` objects, return the map.

## Creating a Map and Adding Markers

`folium.Map(location=...)` and `folium.Marker(location=...)` both require a sequence `[lat, lon]` — **not** a dict. When data uses `{'Lat': ..., 'Lon': ...}` keys, extract them explicitly:

```python
import folium

m = folium.Map(location=[lat, lon], zoom_start=4)

for name, coords in dic.items():
    folium.Marker(
        location=[coords['Lat'], coords['Lon']],
        popup=name
    ).add_to(m)

return m
```

## Building a DataFrame then Mapping Cities

When coordinates are generated with a seeded RNG, generate lon and lat **per city in a loop** — one `np.random.uniform` for longitude then one for latitude. Vectorized bulk generation consumes the RNG in a different order:

```python
import pandas as pd
import numpy as np
import folium

def make_city_map(dic, cities):
    lon_min, lon_max = dic['Lon']
    lat_min, lat_max = dic['Lat']

    data = {'City': [], 'Longitude': [], 'Latitude': []}
    for city in cities:
        data['City'].append(city)
        data['Longitude'].append(np.random.uniform(lon_min, lon_max))
        data['Latitude'].append(np.random.uniform(lat_min, lat_max))

    df = pd.DataFrame(data)
    m = folium.Map(location=[df['Latitude'].iloc[0], df['Longitude'].iloc[0]], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']], popup=row['City']).add_to(m)
    return m, df
```

## Mixing Dict Coordinates and Address Strings

When input values can be `{'Lat': ..., 'Lon': ...}` dicts or plain address strings, use `isinstance` to distinguish them. Call `geocode()` only for string values — not for dict values. Instantiate the geolocator once outside the loop:

```python
from geopy.geocoders import Photon

def map_locations(dic):
    geolocator = Photon(user_agent="geoapiExercises")
    preprocessed = []
    for name, value in dic.items():
        if isinstance(value, dict) and 'Lat' in value and 'Lon' in value:
            lat, lon = value['Lat'], value['Lon']
        elif isinstance(value, str):
            result = geolocator.geocode(value)
            lat, lon = result.latitude, result.longitude
        else:
            raise ValueError(f"Invalid location format for '{name}': {value}")
        preprocessed.append({'Location': name, 'Lat': lat, 'Lon': lon})

    locations_df = pd.DataFrame(preprocessed)
    first = locations_df.iloc[0]
    m = folium.Map(location=[first['Lat'], first['Lon']], zoom_start=4)
    for _, row in locations_df.iterrows():
        folium.Marker([row['Lat'], row['Lon']], popup=row['Location']).add_to(m)
    return m
```

## Computing Pairwise Geodesic Distances

Extract `(lat, lon)` tuples before calling `geodesic`. The canonical approach uses a flat list of tuples indexed by position:

```python
from geopy.distance import geodesic

locations = [(name, v['Lat'], v['Lon']) for name, v in dic.items()]
distances = {}
for i in range(len(locations)):
    for j in range(i + 1, len(locations)):
        d = geodesic(
            (locations[i][1], locations[i][2]),
            (locations[j][1], locations[j][2])
        ).kilometers
        distances[(locations[i][0], locations[j][0])] = d
```

`geodesic()` takes `(lat, lon)` tuples — never a dict.

## Map Object Reference

`m.location` returns the center as `[lat, lon]`. The object type is `folium.folium.Map`.
