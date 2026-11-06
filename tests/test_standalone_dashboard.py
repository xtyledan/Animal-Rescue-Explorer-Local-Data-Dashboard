"""Database-free tests for local dashboard and HTTP responses."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen

from standalone_dashboard import Handler, filter_animals, load_animals


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


if __name__ == "__main__":
    unittest.main()
