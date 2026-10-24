import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailReportCard } from "@/components/avail-report-card";

describe("AvailReportCard", () => {
  it("renders report", () => {
    const { container } = render(
      <AvailReportCard avgUptime={99.725} slaBreaches={1} allSlaMet={false} periodDays={30}
        services={[
          { name: "api", uptimePct: 99.95, downtimeMin: 21.6, slaTarget: 99.9, slaMet: true, incidents: 2 },
          { name: "web", uptimePct: 99.5, downtimeMin: 216, slaTarget: 99.9, slaMet: false, incidents: 5 },
        ]} />
    );
    expect(container.textContent).toContain("Availability (30d)");
    expect(container.textContent).toContain("99.725%");
    expect(container.textContent).toContain("1 breaches");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("web");
    expect(container.textContent).toContain("5 incidents");
  });
});
