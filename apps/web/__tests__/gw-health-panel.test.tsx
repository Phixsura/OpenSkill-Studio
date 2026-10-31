import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwHealthPanel } from "@/components/gw-health-panel";
describe("GwHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwHealthPanel allHealthy={false} avgLatencyMs={24}
        gateways={[
          { name: "gw-1", region: "us-east", status: "healthy", latencyMs: 10 },
          { name: "gw-3", region: "eu-west", status: "degraded", latencyMs: 50 },
        ]} />
    );
    expect(container.textContent).toContain("Gateway Health");
    expect(container.textContent).toContain("Issues");
    expect(container.textContent).toContain("avg 24ms");
    expect(container.textContent).toContain("gw-1");
    expect(container.textContent).toContain("us-east");
  });
});
