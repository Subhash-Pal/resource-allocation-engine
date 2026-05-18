# Resource Allocation Engine

This submission implements the assignment as a local web application for the **Field Service** domain. It compares two dispatch strategies for assigning technicians to service requests while respecting shift windows and skill requirements.

## What is included

- `backend/`: FastAPI API, allocation engine, sample scenario, and test suite
- `frontend/`: React + Vite visualization for side-by-side algorithm comparison
- Two strategies:
  - `greedy`: Processes requests in priority/time order and picks the best currently available technician
  - `optimal_batch`: Uses dynamic programming to choose assignments that maximize the total global score across the entire request set

## Constraint model

Hard constraints:

- Technician must have all required skills
- Request time window must fit inside the technician shift
- A technician can only take one request in the current simplified scenario

Soft constraints used in scoring:

- Higher request priority is preferred
- Shorter travel distance is preferred
- More remaining shift slack after completing the job is preferred

## Why the algorithms differ

The greedy strategy is easy to understand and very fast, but it can spend a versatile technician too early. The batch optimizer considers the whole request set together and can deliberately skip a local best choice if that leads to a higher overall score and better coverage.

## Setup

### One-command PowerShell entrypoint

From the project root:

```powershell
cd .\resource-allocation-engine
powershell -ExecutionPolicy Bypass -File .\run-app.ps1 -Action all
```

Available actions:

- `install`: install backend and frontend dependencies
- `test`: run backend tests and frontend production build
- `verify`: start both services temporarily and confirm the local HTTP endpoints respond
- `run`: start backend and frontend in separate PowerShell windows
- `all`: run `install`, `test`, and `verify`

### Backend

```powershell
cd .\resource-allocation-engine\backend
New-Item -ItemType Directory -Force -Path .\resource-allocation-engine\.tmp,.\resource-allocation-engine\.pip-cache,.\resource-allocation-engine\.pip-target | Out-Null
$env:TMP='.\resource-allocation-engine\.tmp'
$env:TEMP='.\resource-allocation-engine\.tmp'
$env:PIP_CACHE_DIR='.\resource-allocation-engine\.pip-cache'
& 'C:\Users\Shubh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install --target .\resource-allocation-engine\.pip-target -r requirements.txt
$env:PYTHONPATH='.\resource-allocation-engine\.pip-target;.\resource-allocation-engine\backend'
& 'C:\Users\Shubh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### Frontend

```powershell
cd .\resource-allocation-engine\frontend
New-Item -ItemType Directory -Force -Path .\resource-allocation-engine\.npm-cache | Out-Null
$env:npm_config_cache='.\resource-allocation-engine\.npm-cache'
& 'C:\Program Files\nodejs\npm.cmd' install
& 'C:\Program Files\nodejs\npm.cmd' run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## Tests

Run backend tests with:

```powershell
cd .\resource-allocation-engine\backend
$env:PYTHONPATH='.\resource-allocation-engine\.pip-target;.\resource-allocation-engine\backend'
& 'C:\Users\Shubh\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -v
```

## Verification completed

- Backend test suite: `5/5` tests passing
- Frontend production build: successful via `npm run build`
- Output bundle created in `frontend/dist`

## API

- `GET /health`: service health check
- `GET /api/scenario`: sample scenario plus both algorithm outputs
- `POST /api/allocate`: run both algorithms for a supplied scenario payload

## Brief analysis

On the included sample data, the batch optimizer is expected to produce a stronger global plan than the greedy allocator because it protects scarce multi-skill technicians for requests that would otherwise become impossible or much more expensive. Greedy still has value when speed and simple explainability matter more than absolute optimality.
