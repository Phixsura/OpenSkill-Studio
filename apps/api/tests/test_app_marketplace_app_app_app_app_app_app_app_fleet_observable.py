from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_observable import fleet_observable_status
def test_obs():
    r = fleet_observable_status([{"published": True, "cells": 100, "views_24h": 50000}])
    assert r["cells"] == 100
    assert r["all_published"]
