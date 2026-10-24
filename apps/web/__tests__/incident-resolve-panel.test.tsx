import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentResolvePanel } from "@/components/incident-resolve-panel";
describe("IncidentResolvePanel", () => {
  it("renders", () => {
    const { container } = render(
      <IncidentResolvePanel incidentId="inc-1" autoResolve={true} passed={4} total={4}
        checks={{ error_rate_normal: true, latency_normal: true, uptime_restored: true, no_alerts: true }} />
    );
    expect(container.textContent).toContain("Auto-Resolve: inc-1");
    expect(container.textContent).toContain("Ready to resolve");
    expect(container.textContent).toContain("error rate normal");
    expect(container.textContent).toContain("uptime restored");
  });
});
