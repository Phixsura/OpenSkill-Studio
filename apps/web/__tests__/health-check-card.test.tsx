import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthCheckCard from "../src/components/health-check-card";

const healthyProbe = {
  probe_id: "p1",
  endpoint: "/api/health",
  healthy: true,
  consecutive_failures: 0,
  total_checks: 100,
  availability_pct: 99.9,
  last_check_result: "pass" as const,
  last_check_latency_ms: 42,
  last_failure_message: null,
};

const unhealthyProbe = {
  probe_id: "p2",
  endpoint: "/api/payments",
  healthy: false,
  consecutive_failures: 5,
  total_checks: 50,
  availability_pct: 85.0,
  last_check_result: "fail" as const,
  last_check_latency_ms: null,
  last_failure_message: "connection refused",
};

const timeoutProbe = {
  probe_id: "p3",
  endpoint: "/api/search",
  healthy: true,
  consecutive_failures: 1,
  total_checks: 200,
  availability_pct: 98.5,
  last_check_result: "timeout" as const,
  last_check_latency_ms: 5000,
  last_failure_message: null,
};

describe("HealthCheckCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<HealthCheckCard probes={[healthyProbe]} appName="My App" />);
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("My App");
  });

  it("shows overall availability percentage", () => {
    const { container } = render(<HealthCheckCard probes={[healthyProbe]} appName="App" />);
    expect(container.textContent).toContain("99.9%");
  });

  it("shows all-healthy badge when everything is up", () => {
    const { container } = render(<HealthCheckCard probes={[healthyProbe]} appName="App" />);
    expect(container.textContent).toContain("All healthy");
  });

  it("shows unhealthy count badge", () => {
    const { container } = render(
      <HealthCheckCard probes={[healthyProbe, unhealthyProbe]} appName="App" />,
    );
    expect(container.textContent).toContain("1 unhealthy");
  });

  it("renders endpoint names", () => {
    const { container } = render(
      <HealthCheckCard probes={[healthyProbe, unhealthyProbe]} appName="App" />,
    );
    expect(container.textContent).toContain("/api/health");
    expect(container.textContent).toContain("/api/payments");
  });

  it("shows latency for healthy probe", () => {
    const { container } = render(<HealthCheckCard probes={[healthyProbe]} appName="App" />);
    expect(container.textContent).toContain("42ms");
  });

  it("shows result badges", () => {
    const { container } = render(
      <HealthCheckCard probes={[healthyProbe, unhealthyProbe, timeoutProbe]} appName="App" />,
    );
    expect(container.textContent).toContain("Pass");
    expect(container.textContent).toContain("Fail");
    expect(container.textContent).toContain("Timeout");
  });

  it("shows consecutive failures and error message for unhealthy", () => {
    const { container } = render(<HealthCheckCard probes={[unhealthyProbe]} appName="App" />);
    expect(container.textContent).toContain("5 consecutive failures");
    expect(container.textContent).toContain("connection refused");
  });

  it("shows check count and uptime", () => {
    const { container } = render(<HealthCheckCard probes={[healthyProbe]} appName="App" />);
    expect(container.textContent).toContain("100 checks");
    expect(container.textContent).toContain("uptime");
  });

  it("shows empty state when no probes", () => {
    const { container } = render(<HealthCheckCard probes={[]} appName="App" />);
    expect(container.textContent).toContain("No probes configured");
  });
});
