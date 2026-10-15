---
name: geopandas-geodataframe-construction-and
description: GeoDataFrame construction, seeded per-row coordinate generation, Point(lon, lat) convention, CRS, and spatial queries.
---

# geopandas — GeoDataFrame Construction and Geometry

## Creating a GeoDataFrame

Build a GeoDataFrame from a dict by specifying the geometry column name:

```python
import geopandas as gpd
from shapely.geometry import Point

data = {
    'City': ['Rome', 'Athens', 'Cairo'],
    'Coordinates': [Point(12.49, 41.89), Point(23.72, 37.97), Point(31.24, 30.06)],
}
gdf = gpd.GeoDataFrame(data, geometry='Coordinates')
```

The `geometry` parameter must match the column name exactly.

## Generating Random Coordinates with a Seed

Generate coordinates **per row in a loop**, one `np.random.uniform` call for longitude then one for latitude. Vectorized bulk generation (e.g., `np.random.uniform(lo, hi, n)` for all longitudes then all latitudes) consumes the RNG in a different order and produces different values:

```python
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

def make_geo_df(dic, cities):
    lon_min, lon_max = dic['Lon']
    lat_min, lat_max = dic['Lat']

    data = {'City': [], 'Coordinates': []}
    for city in cities:
        data['City'].append(city)
        lon = np.random.uniform(lon_min, lon_max)   # call 1 for this city
        lat = np.random.uniform(lat_min, lat_max)   # call 2 for this city
        data['Coordinates'].append(Point(lon, lat))

    gdf = gpd.GeoDataFrame(data, geometry='Coordinates')
    return gdf
```

## Point Coordinate Convention

`Point(x, y)` — in geographic contexts `x` is **longitude** and `y` is **latitude** (WKT convention, x before y):

```python
p = Point(lon, lat)
p.x   # longitude
p.y   # latitude
```

## CRS and Projections

```python
gdf = gpd.GeoDataFrame(data, geometry='geom', crs='EPSG:4326')
gdf_proj = gdf.to_crs('EPSG:3857')
gdf_proj['area'] = gdf_proj.geometry.area
```

## Spatial Queries

```python
mask = gdf.within(polygon)
subset = gdf[mask]
gdf['distance'] = gdf.geometry.distance(reference_point)
```
