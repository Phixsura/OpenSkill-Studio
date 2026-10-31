from app.services.app_marketplace_extension_geo_index import GeoIndexService


def test_geohash():
    gi = GeoIndexService()
    gh = gi.encode_geohash(37.7749, -122.4194, precision=6)
    assert len(gh) == 6
    # Same location → same geohash
    assert gi.encode_geohash(37.7749, -122.4194) == gh


def test_haversine():
    gi = GeoIndexService()
    # NYC to London ≈ 5570 km
    dist = gi.haversine(40.7128, -74.0060, 51.5074, -0.1278)
    assert 5500 < dist < 5600
    # Same point = 0
    assert gi.haversine(0, 0, 0, 0) == 0


def test_add_and_search():
    gi = GeoIndexService()
    gi.add("sf", 37.7749, -122.4194, {"name": "San Francisco"})
    gi.add("la", 33.9425, -118.4081, {"name": "Los Angeles"})
    gi.add("nyc", 40.7128, -74.0060, {"name": "New York"})
    # Search 100km around SF
    results = gi.search_radius(37.7749, -122.4194, 100)
    ids = [p.id for p, _ in results]
    assert "sf" in ids
    assert "la" not in ids  # ~550km away


def test_knn():
    gi = GeoIndexService()
    gi.add("a", 0, 0)
    gi.add("b", 1, 1)
    gi.add("c", 10, 10)
    gi.add("d", 0.5, 0.5)
    nearest = gi.knn(0, 0, k=2)
    ids = [p.id for p, _ in nearest]
    assert ids[0] == "a"  # closest (distance 0)
    assert ids[1] == "d"  # second closest


def test_bounding_box():
    gi = GeoIndexService()
    gi.add("inside", 40.0, -75.0)
    gi.add("outside", 50.0, -80.0)
    results = gi.bounding_box(39, -76, 41, -74)
    ids = [p.id for p in results]
    assert "inside" in ids
    assert "outside" not in ids


def test_remove():
    gi = GeoIndexService()
    gi.add("x", 0, 0)
    assert gi.size == 1
    gi.remove("x")
    assert gi.size == 0


def test_same_geohash_nearby():
    gi = GeoIndexService()
    gh1 = gi.encode_geohash(37.7749, -122.4194, 4)
    gh2 = gi.encode_geohash(37.7750, -122.4195, 4)
    assert gh1 == gh2  # nearby points share prefix


def test_different_geohash_far():
    gi = GeoIndexService()
    gh1 = gi.encode_geohash(37.7749, -122.4194, 4)
    gh2 = gi.encode_geohash(-33.8688, 151.2093, 4)  # Sydney
    assert gh1 != gh2


def test_zero_radius():
    gi = GeoIndexService()
    gi.add("exact", 10.0, 20.0)
    results = gi.search_radius(10.0, 20.0, 0)
    assert len(results) == 1  # exact match
