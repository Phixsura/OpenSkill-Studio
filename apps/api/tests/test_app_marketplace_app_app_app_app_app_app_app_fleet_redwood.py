from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_redwood import fleet_redwood_status
def test_rw():
    r = fleet_redwood_status([{"deployed": True, "cells": 30, "services": 20}])
    assert r["cells"] == 30
    assert r["all_deployed"]
