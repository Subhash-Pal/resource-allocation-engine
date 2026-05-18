import { useEffect, useState } from "react";

const panelTitles = {
  greedy: "Greedy Allocation",
  optimal_batch: "Optimal Batch Allocation"
};

function MetricCard({ label, value }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function AllocationMap({ resources, requests, result, color }) {
  const requestById = Object.fromEntries(requests.map((request) => [request.id, request]));
  const resourceById = Object.fromEntries(resources.map((resource) => [resource.id, resource]));

  return (
    <svg viewBox="0 0 100 100" className="map-canvas" aria-label={`${result.strategy} map`}>
      <rect x="0" y="0" width="100" height="100" rx="6" className="map-bg" />
      <g className="grid">
        {Array.from({ length: 4 }).map((_, index) => {
          const offset = 20 + index * 20;
          return (
            <g key={offset}>
              <line x1={offset} y1="0" x2={offset} y2="100" />
              <line x1="0" y1={offset} x2="100" y2={offset} />
            </g>
          );
        })}
      </g>
      {result.assignments.map((assignment) => {
        const resource = resourceById[assignment.resource_id];
        const request = requestById[assignment.request_id];
        return (
          <line
            key={`${assignment.resource_id}-${assignment.request_id}`}
            x1={resource.location.x}
            y1={100 - resource.location.y}
            x2={request.location.x}
            y2={100 - request.location.y}
            stroke={color}
            strokeWidth="1.2"
            strokeDasharray="3 2"
          />
        );
      })}
      {resources.map((resource) => (
        <g key={resource.id}>
          <circle
            cx={resource.location.x}
            cy={100 - resource.location.y}
            r="2.7"
            className="resource-dot"
          />
          <text x={resource.location.x + 2.5} y={103 - resource.location.y} className="map-label">
            {resource.name}
          </text>
        </g>
      ))}
      {requests.map((request) => (
        <g key={request.id}>
          <rect
            x={request.location.x - 2}
            y={98 - request.location.y}
            width="4"
            height="4"
            className="request-dot"
          />
          <text x={request.location.x + 2.5} y={103 - request.location.y} className="map-label">
            {request.id}
          </text>
        </g>
      ))}
    </svg>
  );
}

function StrategyPanel({ resources, requests, result, color }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{panelTitles[result.strategy]}</h2>
          <p>{result.assignments.length} assignments generated</p>
        </div>
        <div className="swatch" style={{ backgroundColor: color }} />
      </div>
      <AllocationMap resources={resources} requests={requests} result={result} color={color} />
      <div className="metric-grid">
        <MetricCard label="Coverage" value={`${Math.round(result.metrics.coverage_ratio * 100)}%`} />
        <MetricCard label="Total score" value={result.metrics.total_score} />
        <MetricCard label="Avg distance" value={result.metrics.average_distance} />
        <MetricCard label="Travel" value={result.metrics.total_travel_distance} />
      </div>
      <div className="assignment-list">
        {result.assignments.map((assignment) => (
          <div key={`${assignment.request_id}-${assignment.resource_id}`} className="assignment-item">
            <strong>{assignment.request_id}</strong> {"->"} {assignment.resource_id}
            <span>score {assignment.score}</span>
            <p>{assignment.explanation}</p>
          </div>
        ))}
        {result.unassigned_requests.map((item) => (
          <div key={item.request_id} className="assignment-item unassigned">
            <strong>{item.request_id}</strong> unassigned
            <p>{item.reason}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    fetch("/api/scenario")
      .then((response) => response.json())
      .then((payload) => {
        setData(payload);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  if (status === "loading") {
    return <div className="state-screen">Loading allocation engine...</div>;
  }

  if (status === "error") {
    return <div className="state-screen">Could not reach the backend service.</div>;
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">{data.scenario.domain} dispatch simulation</p>
          <h1>Resource Allocation Engine</h1>
          <p className="hero-copy">
            Compare a fast greedy allocator against a globally optimized batch strategy for
            technician dispatch requests.
          </p>
        </div>
        <div className="hero-aside">
          <MetricCard label="Technicians" value={data.scenario.resources.length} />
          <MetricCard label="Requests" value={data.scenario.requests.length} />
        </div>
      </section>

      <section className="analysis-strip">
        <h2>Comparison insight</h2>
        <p>{data.analysis}</p>
      </section>

      <section className="panel-grid">
        <StrategyPanel
          resources={data.scenario.resources}
          requests={data.scenario.requests}
          result={data.results.greedy}
          color="#ff7a18"
        />
        <StrategyPanel
          resources={data.scenario.resources}
          requests={data.scenario.requests}
          result={data.results.optimal_batch}
          color="#0ea5e9"
        />
      </section>
    </main>
  );
}
