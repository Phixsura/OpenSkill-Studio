import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-endpoint-health-probe-card";

describe("HealthProbeCard", () => {
  it("shows probes", () => {
    const probes = [{ probe_id: "p1", endpoint: "/health", current_status: "healthy", consecutive_healthy: 5, consecutive_unhealthy: 0 }];
    const { container } = render(<Card probes={probes} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Health Probes");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("healthy");
  });
  it("shows unhealthy alert", () => {
    const probes = [{ probe_id: "p1", endpoint: "/api", current_status: "unhealthy", consecutive_healthy: 0, consecutive_unhealthy: 3 }];
    const { container } = render(<Card probes={probes} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("1 down");
  });
});
