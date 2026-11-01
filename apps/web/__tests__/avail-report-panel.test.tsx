import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailReportPanel } from "@/components/avail-report-panel";
describe("AvailReportPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AvailReportPanel period="October 2026" avgUptimePct={99.745} totalDowntimeMinutes={221}
        totalIncidents={4} slaBreaches={1} allSlaMet={false}
        services={[
          { service: "db", uptimePct: 99.5, downtimeMin: 216, slaMet: false },
          { service: "api", uptimePct: 99.99, downtimeMin: 5, slaMet: true },
        ]} />
    );
    expect(container.textContent).toContain("Availability Report — October 2026");
    expect(container.textContent).toContain("99.745% avg");
    expect(container.textContent).toContain("1 SLA breach");
    expect(container.textContent).toContain("221min");
    expect(container.textContent).toContain("4");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("99.5%");
  });
});
