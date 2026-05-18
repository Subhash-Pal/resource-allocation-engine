# Run The Application

This file contains only the steps needed to run the project locally.

## Project location

```powershell
cd .\resource-allocation-engine
```

## First-time setup and verification

Run this once to install dependencies, run tests, build the frontend, and verify both services can start:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-app.ps1
```

## Start the application

Run this when you want to launch the app for normal use:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-app.ps1 -Action run
```

This opens two PowerShell windows:

- backend on `http://127.0.0.1:8000`
- frontend on `http://127.0.0.1:5173`

## Open in browser

Use these URLs:

- React app: `http://127.0.0.1:5173`
- backend health check: `http://127.0.0.1:8000/health`
- backend sample API: `http://127.0.0.1:8000/api/scenario`

## Useful commands

Install dependencies only:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-app.ps1 -Action install
```

Run tests only:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-app.ps1 -Action test
```

Run startup verification only:

```powershell
powershell -ExecutionPolicy Bypass -File .\run-app.ps1 -Action verify
```

## Stop the application

Close the two PowerShell windows opened by `-Action run`, or press `Ctrl + C` in those windows.
