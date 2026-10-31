import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthCheckCard from "../src/components/health-check-card";

const endpoints = [
  {
    endpoint_id: "api",
    url: "https://api.example.com/health",
    current_status: "up" as const,
    uptime_pct: 99.5,
    avg_latency_ms: 45,
  },
  {
    endpoint_id: "db",
    url: "https://db.example.com/health",
    current_status: "down" as const,
    uptime_pct: 85.0,
    avg_latency_ms: 120,
  },
  {
    endpoint_id: "cache",
    url: "https://cache/ping",
    current_status: "degraded" as const,
    uptime_pct: 92.3,
    avg_latency_ms: 200,
  },
];

describe("HealthCheckCard", () => {
  it("renders header and count", () => {
    const { container } = render(<HealthCheckCard endpoints={endpoints} appName="My App" />);
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("3 endpoints");
  });

  it("shows down count", () => {
    const { container } = render(<HealthCheckCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("1 down");
  });

  it("shows uptime percentages", () => {
    const { container } = render(<HealthCheckCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("99.5% uptime");
    expect(container.textContent).toContain("85% uptime");
  });

  it("shows latency", () => {
    const { container } = render(<HealthCheckCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("45ms avg");
    expect(container.textContent).toContain("120ms avg");
  });

  it("shows empty state", () => {
    const { container } = render(<HealthCheckCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No health checks");
  });
});
