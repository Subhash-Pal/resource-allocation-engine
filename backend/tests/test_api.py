import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_sample_scenario_endpoint(self) -> None:
        response = self.client.get("/api/scenario")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scenario"]["domain"], "Field Service")
        self.assertIn("greedy", payload["results"])
        self.assertIn("optimal_batch", payload["results"])


if __name__ == "__main__":
    unittest.main()
