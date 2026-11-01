import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CapacityAlertPanel } from "@/components/capacity-alert-panel";
describe("CapacityAlertPanel", () => {
  it("renders alerts", () => {
    const { container } = render(
      <CapacityAlertPanel critical={1} servicesChecked={3}
        alerts={[
          { service: "api", severity: "critical", bottleneck: "cpu", utilization: 95 },
          { service: "db", severity: "warning", bottleneck: "memory", utilization: 85 },
        ]} />
    );
    expect(container.textContent).toContain("Capacity Alerts");
    expect(container.textContent).toContain("2 alerts (1 critical)");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("cpu at 95%");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("memory at 85%");
  });
});
