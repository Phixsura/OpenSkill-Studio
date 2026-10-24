import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LatencySloPanelComponent } from "@/components/latency-slo-panel";
describe("LatencySloPanelComponent", () => {
  it("renders", () => {
    const { container } = render(
      <LatencySloPanelComponent compliancePct={66.7} met={2} breached={1}
        endpoints={[
          { endpoint: "/api/users", p99Ms: 100, targetMs: 200, met: true, headroomMs: 100 },
          { endpoint: "/api/reports", p99Ms: 800, targetMs: 500, met: false, headroomMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Latency SLO");
    expect(container.textContent).toContain("66.7% compliant");
    expect(container.textContent).toContain("2 met");
    expect(container.textContent).toContain("1 breached");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("100ms / 200ms");
    expect(container.textContent).toContain("+100ms");
  });
});
