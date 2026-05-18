import unittest

from app.engine import (
    compare_algorithms,
    greedy_allocate,
    optimal_batch_allocate,
    score_candidate,
)
from app.models import Coordinate, Request, Resource, Scenario


class AllocationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = Scenario(
            resources=[
                Resource(
                    id="r1",
                    name="Near generalist",
                    location=Coordinate(x=0, y=0),
                    skills=["electrical", "hvac"],
                    shift_start=8,
                    shift_end=17,
                ),
                Resource(
                    id="r2",
                    name="Far specialist",
                    location=Coordinate(x=10, y=0),
                    skills=["electrical"],
                    shift_start=8,
                    shift_end=17,
                ),
            ],
            requests=[
                Request(
                    id="q1",
                    title="General electrical fix",
                    location=Coordinate(x=1, y=0),
                    required_skills=["electrical"],
                    start_hour=9,
                    end_hour=10,
                    priority=5,
                ),
                Request(
                    id="q2",
                    title="HVAC failure",
                    location=Coordinate(x=2, y=0),
                    required_skills=["hvac"],
                    start_hour=9,
                    end_hour=10,
                    priority=5,
                ),
            ],
        )

    def test_candidate_requires_matching_skills(self) -> None:
        candidate = score_candidate(self.scenario.resources[1], self.scenario.requests[1])
        self.assertIsNone(candidate)

    def test_batch_optimizer_can_outperform_greedy(self) -> None:
        greedy = greedy_allocate(self.scenario)
        batch = optimal_batch_allocate(self.scenario)

        self.assertEqual(greedy.metrics.assigned_requests, 1)
        self.assertEqual(batch.metrics.assigned_requests, 2)
        self.assertGreater(batch.metrics.total_score, greedy.metrics.total_score)

    def test_comparison_returns_both_strategies(self) -> None:
        results = compare_algorithms(self.scenario)
        self.assertIn("greedy", {key.value for key in results.keys()})
        self.assertIn("optimal_batch", {key.value for key in results.keys()})


if __name__ == "__main__":
    unittest.main()
