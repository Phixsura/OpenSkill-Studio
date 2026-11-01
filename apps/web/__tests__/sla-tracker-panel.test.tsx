import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SlaTrackerPanel } from "@/components/sla-tracker-panel";
describe("SlaTrackerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SlaTrackerPanel compliancePct={50}
        services={[
          { service: "api", compliant: true, uptimePct: 99.99, p99Ms: 150 },
          { service: "db", compliant: false, uptimePct: 99.0, p99Ms: 250 },
        ]} />
    );
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("99.99%");
  });
});
