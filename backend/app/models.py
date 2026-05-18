from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AllocationStrategy(str, Enum):
    GREEDY = "greedy"
    OPTIMAL_BATCH = "optimal_batch"


class Coordinate(BaseModel):
    x: float
    y: float


class Resource(BaseModel):
    id: str
    name: str
    location: Coordinate
    skills: List[str]
    shift_start: int = Field(ge=0, le=24)
    shift_end: int = Field(ge=0, le=24)
    max_jobs: int = Field(default=1, ge=1)


class Request(BaseModel):
    id: str
    title: str
    location: Coordinate
    required_skills: List[str]
    start_hour: int = Field(ge=0, le=24)
    end_hour: int = Field(ge=0, le=24)
    priority: int = Field(default=1, ge=1, le=5)
    estimated_duration: int = Field(default=1, ge=1, le=8)


class Assignment(BaseModel):
    request_id: str
    resource_id: str
    score: float
    distance: float
    explanation: str


class UnassignedRequest(BaseModel):
    request_id: str
    reason: str


class AllocationMetrics(BaseModel):
    assigned_requests: int
    unassigned_requests: int
    coverage_ratio: float
    total_score: float
    average_distance: float
    total_travel_distance: float


class AllocationResult(BaseModel):
    strategy: AllocationStrategy
    assignments: List[Assignment]
    unassigned_requests: List[UnassignedRequest]
    metrics: AllocationMetrics


class Scenario(BaseModel):
    domain: str = "Field Service"
    resources: List[Resource]
    requests: List[Request]


class ComparisonResponse(BaseModel):
    scenario: Scenario
    results: Dict[AllocationStrategy, AllocationResult]
    analysis: str


class AllocationRequest(BaseModel):
    scenario: Optional[Scenario] = None
