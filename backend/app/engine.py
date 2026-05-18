from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .models import (
    AllocationMetrics,
    AllocationResult,
    AllocationStrategy,
    Assignment,
    Request,
    Resource,
    Scenario,
    UnassignedRequest,
)


@dataclass(frozen=True)
class Candidate:
    resource: Resource
    request: Request
    score: float
    distance: float
    explanation: str


def distance_between(resource: Resource, request: Request) -> float:
    return math.dist(
        (resource.location.x, resource.location.y),
        (request.location.x, request.location.y),
    )


def is_feasible(resource: Resource, request: Request) -> Tuple[bool, str]:
    missing_skills = sorted(set(request.required_skills) - set(resource.skills))
    if missing_skills:
        return False, f"Missing skills: {', '.join(missing_skills)}"
    if request.start_hour < resource.shift_start or request.end_hour > resource.shift_end:
        return False, "Request falls outside technician shift window"
    return True, "Eligible"


def score_candidate(resource: Resource, request: Request) -> Candidate | None:
    feasible, reason = is_feasible(resource, request)
    if not feasible:
        return None

    distance = distance_between(resource, request)
    skill_bonus = 12 * len(request.required_skills)
    priority_bonus = 20 * request.priority
    slack_bonus = max(0, (resource.shift_end - request.end_hour)) * 1.5
    distance_penalty = distance * 1.8
    score = round(priority_bonus + skill_bonus + slack_bonus - distance_penalty, 2)
    explanation = (
        f"Priority {request.priority} request, travel distance {distance:.1f}, "
        f"skills matched: {', '.join(request.required_skills)}"
    )
    return Candidate(
        resource=resource,
        request=request,
        score=score,
        distance=round(distance, 2),
        explanation=explanation,
    )


def build_candidates(scenario: Scenario) -> Dict[tuple[str, str], Candidate]:
    candidates: Dict[tuple[str, str], Candidate] = {}
    for resource in scenario.resources:
        for request in scenario.requests:
            candidate = score_candidate(resource, request)
            if candidate:
                candidates[(resource.id, request.id)] = candidate
    return candidates


def greedy_allocate(scenario: Scenario) -> AllocationResult:
    candidates = build_candidates(scenario)
    available = {resource.id for resource in scenario.resources}
    assignments: List[Assignment] = []
    unassigned: List[UnassignedRequest] = []

    ordered_requests = sorted(
        scenario.requests,
        key=lambda request: (-request.priority, request.start_hour, request.id),
    )

    for request in ordered_requests:
        feasible_candidates = [
            candidate
            for (resource_id, request_id), candidate in candidates.items()
            if request_id == request.id and resource_id in available
        ]
        if not feasible_candidates:
            unassigned.append(
                UnassignedRequest(
                    request_id=request.id,
                    reason="No available technician satisfies the hard constraints",
                )
            )
            continue

        chosen = max(
            feasible_candidates,
            key=lambda candidate: (candidate.score, -candidate.distance, candidate.resource.id),
        )
        available.remove(chosen.resource.id)
        assignments.append(
            Assignment(
                request_id=chosen.request.id,
                resource_id=chosen.resource.id,
                score=chosen.score,
                distance=chosen.distance,
                explanation=chosen.explanation,
            )
        )

    return AllocationResult(
        strategy=AllocationStrategy.GREEDY,
        assignments=assignments,
        unassigned_requests=unassigned,
        metrics=build_metrics(scenario, assignments, unassigned),
    )


def optimal_batch_allocate(scenario: Scenario) -> AllocationResult:
    candidates = build_candidates(scenario)
    resources = scenario.resources
    requests = scenario.requests
    resource_index = {resource.id: idx for idx, resource in enumerate(resources)}
    request_index = {request.id: idx for idx, request in enumerate(requests)}
    memo: Dict[tuple[int, int], tuple[float, List[Assignment]]] = {}

    def solve(request_pos: int, used_mask: int) -> tuple[float, List[Assignment]]:
        key = (request_pos, used_mask)
        if key in memo:
            return memo[key]

        if request_pos == len(requests):
            return 0.0, []

        request = requests[request_pos]
        best_score, best_assignments = solve(request_pos + 1, used_mask)

        for resource in resources:
            bit = 1 << resource_index[resource.id]
            if used_mask & bit:
                continue
            candidate = candidates.get((resource.id, request.id))
            if not candidate:
                continue

            future_score, future_assignments = solve(request_pos + 1, used_mask | bit)
            total_score = candidate.score + future_score
            if total_score > best_score:
                best_score = total_score
                best_assignments = [
                    Assignment(
                        request_id=request.id,
                        resource_id=resource.id,
                        score=candidate.score,
                        distance=candidate.distance,
                        explanation=(
                            f"{candidate.explanation}. Chosen by batch optimizer for global score."
                        ),
                    )
                ] + future_assignments

        memo[key] = (best_score, best_assignments)
        return memo[key]

    _, assignments = solve(0, 0)
    assigned_request_ids = {assignment.request_id for assignment in assignments}
    unassigned: List[UnassignedRequest] = []
    for request in requests:
        if request.id in assigned_request_ids:
            continue
        feasible_any = any(
            (resource.id, request.id) in candidates for resource in resources
        )
        reason = (
            "Left unassigned to preserve a better global plan"
            if feasible_any
            else "No technician satisfies the hard constraints"
        )
        unassigned.append(UnassignedRequest(request_id=request.id, reason=reason))

    assignments.sort(key=lambda assignment: request_index[assignment.request_id])
    return AllocationResult(
        strategy=AllocationStrategy.OPTIMAL_BATCH,
        assignments=assignments,
        unassigned_requests=unassigned,
        metrics=build_metrics(scenario, assignments, unassigned),
    )


def build_metrics(
    scenario: Scenario,
    assignments: List[Assignment],
    unassigned: List[UnassignedRequest],
) -> AllocationMetrics:
    total_distance = round(sum(assignment.distance for assignment in assignments), 2)
    total_score = round(sum(assignment.score for assignment in assignments), 2)
    assigned_requests = len(assignments)
    request_count = len(scenario.requests)
    return AllocationMetrics(
        assigned_requests=assigned_requests,
        unassigned_requests=len(unassigned),
        coverage_ratio=round(assigned_requests / request_count, 2) if request_count else 0.0,
        total_score=total_score,
        average_distance=round(total_distance / assigned_requests, 2) if assigned_requests else 0.0,
        total_travel_distance=total_distance,
    )


def compare_algorithms(scenario: Scenario) -> Dict[AllocationStrategy, AllocationResult]:
    return {
        AllocationStrategy.GREEDY: greedy_allocate(scenario),
        AllocationStrategy.OPTIMAL_BATCH: optimal_batch_allocate(scenario),
    }


def summarize_comparison(results: Dict[AllocationStrategy, AllocationResult]) -> str:
    greedy = results[AllocationStrategy.GREEDY].metrics
    batch = results[AllocationStrategy.OPTIMAL_BATCH].metrics

    if batch.total_score > greedy.total_score:
        lead = "The batch optimizer produces the stronger global plan"
    elif batch.total_score < greedy.total_score:
        lead = "The greedy allocator edges out the batch optimizer on this scenario"
    else:
        lead = "Both strategies tie on total score for this scenario"

    return (
        f"{lead}. Greedy score: {greedy.total_score}, batch score: {batch.total_score}. "
        f"Greedy coverage: {greedy.coverage_ratio:.0%}, batch coverage: {batch.coverage_ratio:.0%}. "
        "Greedy is faster and easier to explain request-by-request, while the batch optimizer can "
        "sacrifice a local win to improve overall assignment quality."
    )
