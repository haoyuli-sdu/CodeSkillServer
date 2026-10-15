---
name: geopy-distance-calculation-and-geocoding
description: 'geopy patterns: geodesic distance from (lat,lon) tuples, pairwise distance computation, Photon geocoding, and mixed dict/string input handling.'
---

# geopy — Distance Calculation and Geocoding

## Geodesic Distance

`geodesic` takes coordinate tuples `(lat, lon)` — never dicts or lists with named keys:

```python
from geopy.distance import geodesic

dist = geodesic((48.8566, 2.3522), (51.5074, -0.1278)).kilometers
# .miles and .meters are also available
```

## Pairwise Distances Between Locations

When the input is a dict like `{'City': {'Lat': ..., 'Lon': ...}, ...}`, extract tuples before calling `geodesic`. The canonical pattern uses a flat list of `(name, lat, lon)` tuples:

```python
def compute_distances(dic):
    if not dic:
        raise ValueError("Input dictionary is empty.")
    locations = [(k, v['Lat'], v['Lon']) for k, v in dic.items()]
    distances = {}
    for i in range(len(locations)):
        for j in range(i + 1, len(locations)):
            d = geodesic(
                (locations[i][1], locations[i][2]),
                (locations[j][1], locations[j][2])
            ).kilometers
            distances[(locations[i][0], locations[j][0])] = d
    return distances
```

## Geocoding with Photon

`Photon` converts address strings to coordinates. Always pass a `user_agent` string:

```python
from geopy.geocoders import Photon

geolocator = Photon(user_agent="geoapiExercises")
result = geolocator.geocode("Berlin, Germany")
lat, lon = result.latitude, result.longitude
```

## Mixed Input (coordinates or address strings)

When input values are either coordinate dicts `{'Lat': ..., 'Lon': ...}` or plain address strings, use `isinstance` to distinguish them. Instantiate the geolocator **once** outside the loop, and call `geocode()` only for string values — not for dict values:

```python
def preprocess_locations(dic):
    geolocator = Photon(user_agent="geoapiExercises")
    locations = []
    for name, value in dic.items():
        if isinstance(value, dict) and 'Lat' in value and 'Lon' in value:
            lat, lon = value['Lat'], value['Lon']
        elif isinstance(value, str):
            result = geolocator.geocode(value)
            lat, lon = result.latitude, result.longitude
        else:
            raise ValueError(f"Invalid location format for '{name}': {value}")
        locations.append({'Location': name, 'Lat': lat, 'Lon': lon})
    return locations
```

Calling `geocode()` on a dict value instead of only on string values causes the geocoder to be invoked the wrong number of times.
