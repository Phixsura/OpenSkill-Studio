import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiHealthCheckSchedulerCard from "../src/components/api-developer-api-api-health-check-scheduler-card";

const checks = [
  { check_id: "c1", endpoint: "/health", interval_seconds: 30, last_result: "healthy", consecutive_failures: 0, enabled: true },
  { check_id: "c2", endpoint: "/api/db", interval_seconds: 60, last_result: "unhealthy", consecutive_failures: 3, enabled: true },
];

describe("APIDeveloperAPIApiHealthCheckSchedulerCard", () => {
  it("shows health checks", () => {
    const { container } = render(<APIDeveloperAPIApiHealthCheckSchedulerCard checks={checks} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("every 30s");
    expect(container.textContent).toContain("3 fails");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiHealthCheckSchedulerCard checks={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No health checks");
  });
});
