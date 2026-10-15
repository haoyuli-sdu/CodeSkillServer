---
name: shapely-geometric-objects-and-spatial-op
description: 'shapely core types: Point(lon,lat) convention, LineString, Polygon, spatial predicates, and sequential per-point coordinate generation.'
---

# shapely — Geometric Objects and Spatial Operations

## Core Geometry Types

```python
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
```

**Point**: `Point(x, y)` — in geographic contexts `x` is **longitude** and `y` is **latitude** (WKT/GIS convention, x before y):

```python
p = Point(2.35, 48.85)   # (longitude, latitude)
p.x   # 2.35  (longitude)
p.y   # 48.85 (latitude)
str(p)  # 'POINT (2.35 48.85)'
```

**LineString**: sequence of `(x, y)` tuples:

```python
line = LineString([(0, 0), (1, 1), (2, 0)])
line.length   # Euclidean length
```

**Polygon**: exterior ring, optionally with interior holes:

```python
poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
poly.area      # 1.0
poly.length    # perimeter, 4.0
```

## Spatial Predicates

```python
poly.contains(point)     # True if point strictly inside
poly.intersects(other)   # True if geometries share any space
poly.within(other)       # True if self is entirely inside other
geom1.distance(geom2)    # minimum distance between geometries
```

## Constructing Points for a GeoDataFrame

When building Points with a seeded RNG, generate lon and lat sequentially per point — not as separate arrays. Vectorized bulk calls consume the RNG in a different order:

```python
import numpy as np
from shapely.geometry import Point

for city in cities:
    lon = np.random.uniform(lon_min, lon_max)
    lat = np.random.uniform(lat_min, lat_max)
    point = Point(lon, lat)   # x=lon, y=lat
```

## Common Operations

```python
centroid = poly.centroid          # returns a Point
hull = MultiPolygon([p1, p2]).convex_hull
buffered = point.buffer(1.0)      # circle of radius 1
inter = poly1.intersection(poly2) # Polygon or empty geometry
```

## Return Types

| Operation | Returns |
|---|---|
| `Point(x, y)` | `Point` |
| `poly.centroid` | `Point` |
| `poly.intersection(other)` | `Polygon` / `MultiPolygon` / `GeometryCollection` |
| `poly.union(other)` | `Polygon` / `MultiPolygon` |
| `poly.buffer(r)` | `Polygon` |
| `geom.distance(other)` | `float` |
