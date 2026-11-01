"""Geo Index — spatial indexing for geolocation queries.

Implements:
- Geohash encoding/decoding for spatial partitioning
- Proximity search (find all within radius)
- Haversine distance calculation
- K-nearest neighbors
- Bounding box queries
"""
from __future__ import annotations
from dataclasses import dataclass
import math

GEOHASH_CHARS = "0123456789bcdefghjkmnpqrstuvwxyz"


@dataclass
class GeoPoint:
    id: str
    lat: float
    lon: float
    data: dict | None = None
    geohash: str = ""


class GeoIndexService:
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, precision: int = 6):
        self._precision = precision
        self._points: dict[str, GeoPoint] = {}
        self._hash_index: dict[str, list[str]] = {}  # geohash prefix → [point_ids]

    def encode_geohash(self, lat: float, lon: float,
                       precision: int = 0) -> str:
        """Encode lat/lon to geohash string."""
        precision = precision or self._precision
        lat_range = [-90.0, 90.0]
        lon_range = [-180.0, 180.0]
        bits = 0
        bit_count = 0
        hash_chars = []
        is_lon = True

        while len(hash_chars) < precision:
            if is_lon:
                mid = (lon_range[0] + lon_range[1]) / 2
                if lon >= mid:
                    bits = (bits << 1) | 1
                    lon_range[0] = mid
                else:
                    bits = bits << 1
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                if lat >= mid:
                    bits = (bits << 1) | 1
                    lat_range[0] = mid
                else:
                    bits = bits << 1
                    lat_range[1] = mid
            is_lon = not is_lon
            bit_count += 1
            if bit_count == 5:
                hash_chars.append(GEOHASH_CHARS[bits])
                bits = 0
                bit_count = 0

        return "".join(hash_chars)

    def haversine(self, lat1: float, lon1: float,
                  lat2: float, lon2: float) -> float:
        """Distance in km between two points using Haversine formula."""
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return self.EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))

    def add(self, point_id: str, lat: float, lon: float,
            data: dict | None = None) -> GeoPoint:
        gh = self.encode_geohash(lat, lon)
        point = GeoPoint(id=point_id, lat=lat, lon=lon, data=data, geohash=gh)
        self._points[point_id] = point
        # Index by geohash prefixes for fast proximity
        for i in range(1, len(gh) + 1):
            prefix = gh[:i]
            if prefix not in self._hash_index:
                self._hash_index[prefix] = []
            self._hash_index[prefix].append(point_id)
        return point

    def search_radius(self, lat: float, lon: float,
                      radius_km: float) -> list[tuple[GeoPoint, float]]:
        """Find all points within radius_km. Returns [(point, distance)]."""
        results = []
        for point in self._points.values():
            dist = self.haversine(lat, lon, point.lat, point.lon)
            if dist <= radius_km:
                results.append((point, round(dist, 3)))
        results.sort(key=lambda x: x[1])
        return results

    def knn(self, lat: float, lon: float, k: int = 5) -> list[tuple[GeoPoint, float]]:
        """K-nearest neighbors."""
        scored = [(p, self.haversine(lat, lon, p.lat, p.lon))
                  for p in self._points.values()]
        scored.sort(key=lambda x: x[1])
        return [(p, round(d, 3)) for p, d in scored[:k]]

    def bounding_box(self, min_lat: float, min_lon: float,
                     max_lat: float, max_lon: float) -> list[GeoPoint]:
        """Find points within a bounding box."""
        return [p for p in self._points.values()
                if min_lat <= p.lat <= max_lat and min_lon <= p.lon <= max_lon]

    def remove(self, point_id: str) -> bool:
        return self._points.pop(point_id, None) is not None

    @property
    def size(self) -> int:
        return len(self._points)
