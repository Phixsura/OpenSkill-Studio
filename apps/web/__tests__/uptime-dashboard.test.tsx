import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UptimeDashboard } from "@/components/uptime-dashboard";

describe("UptimeDashboard", () => {
  it("renders monitors", () => {
    const { container } = render(
      <UptimeDashboard avgUptime={99.745} allSlaMet={false} monitors={[
        { name: "API", uptimePct: 99.99, slaMet: true, totalChecks: 1000, downPeriods: 1 },
        { name: "Database", uptimePct: 99.5, slaMet: false, totalChecks: 1000, downPeriods: 5 },
      ]} />
    );
    expect(container.textContent).toContain("Uptime Monitor");
    expect(container.textContent).toContain("99.745%");
    expect(container.textContent).toContain("SLA Issues");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("5 incidents");
  });
});
