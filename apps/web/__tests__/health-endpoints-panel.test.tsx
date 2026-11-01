import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthEndpointsPanel } from "@/components/health-endpoints-panel";
describe("HealthEndpointsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HealthEndpointsPanel healthy={1} total={2}
        endpoints={[
          { service: "api", url: "/health", healthy: true, lastLatencyMs: 5, consecutiveFailures: 0 },
          { service: "db", url: "/health", healthy: false, lastLatencyMs: 100, consecutiveFailures: 3 },
        ]} />
    );
    expect(container.textContent).toContain("Health Endpoints");
    expect(container.textContent).toContain("1/2 healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("5ms");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("3 fails");
  });
});
