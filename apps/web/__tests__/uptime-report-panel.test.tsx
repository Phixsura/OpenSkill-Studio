import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeReportPanel } from "@/components/uptime-report-panel";
describe("UptimeReportPanel", () => {
  it("renders", () => {
    const { container } = render(
      <UptimeReportPanel period="October 2026" avgUptimePct={99.83} allSlaMet={false}
        services={[
          { service: "api", uptimePct: 99.99, incidents: 1, downtimeMinutes: 5, slaMet: true },
          { service: "worker", uptimePct: 99.5, incidents: 3, downtimeMinutes: 216, slaMet: false },
        ]} />
    );
    expect(container.textContent).toContain("Uptime Report — October 2026");
    expect(container.textContent).toContain("avg 99.83%");
    expect(container.textContent).toContain("SLA breached");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("216min down");
  });
});
