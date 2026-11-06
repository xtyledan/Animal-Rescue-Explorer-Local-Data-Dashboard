"""Database-free tests for local dashboard and HTTP responses."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from unittest.mock import patch, MagicMock
import os

from standalone_dashboard import Handler, filter_animals, load_animals, PAGE


class DashboardTests(unittest.TestCase):
    def test_bundled_data(self):
        rows = load_animals()
        self.assertGreaterEqual(len(rows), 5)
        self.assertTrue(all(row["animal_id"].startswith("DEMO-") for row in rows))

    def test_filter_by_type(self):
        rows = load_animals()
        filtered = filter_animals(rows, animal_type="dog")
        self.assertTrue(filtered)
        self.assertTrue(all(row["animal_type"] == "Dog" for row in filtered))

    def test_filter_by_breed(self):
        filtered = filter_animals(load_animals(), breed="labrador")
        self.assertGreaterEqual(len(filtered), 1)
        self.assertTrue(all("Labrador" in row["breed"] for row in filtered))

    def test_filter_by_outcome(self):
        filtered = filter_animals(load_animals(), outcome="adoption")
        self.assertTrue(all(row["outcome_type"] == "Adoption" for row in filtered))

    def test_combined_filter(self):
        filtered = filter_animals(load_animals(), "Dog", "Labrador", "Adoption")
        self.assertEqual([row["animal_id"] for row in filtered], ["DEMO-001"])

    def test_http_health_api_and_html(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with urlopen(base + "/health", timeout=4) as resp:
                self.assertEqual(json.load(resp), {"status": "ok"})
            with urlopen(base + "/api/animals?animal_type=Dog&breed=labrador", timeout=4) as resp:
                data = json.load(resp)
                self.assertEqual(data["source"], "sample")
                self.assertEqual(len(data["animals"]), 2)
            with urlopen(base + "/", timeout=4) as resp:
                html = resp.read().decode("utf-8")
                self.assertIn("Animal Rescue Explorer", html)
                self.assertIn("Synthetic", html)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=4)

    def test_missing_mongodb_coordinates_are_not_zero(self):
        fake = MagicMock()
        fake.read.return_value = [
            {"animal_id": "A1", "name": "Unknown", "location_lat": None,
             "location_long": None},
            {"animal_id": "A2", "name": "Equator", "location_lat": 0,
             "location_long": 0},
        ]
        with patch.dict(os.environ, {"MONGO_URI": "mongodb://example.invalid"}):
            with patch("crud.AnimalShelter", return_value=fake):
                result = load_animals()
        self.assertEqual(result[0]["location_lat"], "")
        self.assertEqual(result[0]["location_long"], "")
        self.assertEqual(result[1]["location_lat"], 0)
        self.assertEqual(result[1]["location_long"], 0)

    def test_client_requires_present_coordinates_before_map_link(self):
        # The browser also rejects null/undefined coordinates independent
        # of the server's response normalization.
        self.assertIn("r.location_lat!==null", PAGE)
        self.assertIn("r.location_long!==null", PAGE)
        self.assertIn("r.location_lat!==undefined", PAGE)
        self.assertIn("r.location_long!==undefined", PAGE)


if __name__ == "__main__":
    unittest.main()
