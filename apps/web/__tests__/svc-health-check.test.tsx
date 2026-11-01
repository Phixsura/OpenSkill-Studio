import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcHealthCheck } from "@/components/svc-health-check";

describe("SvcHealthCheck", () => {
  it("renders", () => {
    const { container } = render(
      <SvcHealthCheck overall="degraded" healthPct={50} healthy={1} unhealthy={1}
        results={[
          { service: "api", healthy: true, checksPassed: 2, checksTotal: 2, latencyMs: 5 },
          { service: "worker", healthy: false, checksPassed: 1, checksTotal: 2, latencyMs: 10 },
        ]} />
    );
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("degraded");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("2/2");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("1/2");
  });
});
