from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_marimo import fleet_marimo_status
def test_mar():
    r = fleet_marimo_status([{"running": True, "cells": 200, "users_24h": 5000}])
    assert r["cells"] == 200
    assert r["all_running"]
