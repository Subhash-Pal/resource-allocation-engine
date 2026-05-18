from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import compare_algorithms, summarize_comparison
from .models import AllocationRequest, ComparisonResponse
from .sample_data import build_sample_scenario

app = FastAPI(title="Resource Allocation Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/scenario", response_model=ComparisonResponse)
def get_sample_comparison() -> ComparisonResponse:
    scenario = build_sample_scenario()
    results = compare_algorithms(scenario)
    return ComparisonResponse(
        scenario=scenario,
        results=results,
        analysis=summarize_comparison(results),
    )


@app.post("/api/allocate", response_model=ComparisonResponse)
def allocate(payload: AllocationRequest) -> ComparisonResponse:
    scenario = payload.scenario or build_sample_scenario()
    results = compare_algorithms(scenario)
    return ComparisonResponse(
        scenario=scenario,
        results=results,
        analysis=summarize_comparison(results),
    )
