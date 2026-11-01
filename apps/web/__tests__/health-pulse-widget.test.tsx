import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthPulseWidget } from "@/components/health-pulse-widget";

describe("HealthPulseWidget", () => {
  it("renders pulse", () => {
    const { container } = render(
      <HealthPulseWidget status="healthy" emoji="💚" scoreDisplay="100%"
        checks={{ api: true, database: true, cache: true }}
        summary="💚 HEALTHY" activeIncidents={0} errorRatePct={0.1} p99LatencyMs={85} />
    );
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("0.1%");
    expect(container.textContent).toContain("85ms");
  });
});
