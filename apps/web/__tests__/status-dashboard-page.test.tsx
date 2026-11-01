import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusDashboardPage } from "@/components/status-dashboard-page";

describe("StatusDashboardPage", () => {
  it("operational", () => {
    const { container } = render(
      <StatusDashboardPage overallStatus="operational" uptimePct={99.99}
        services={[{ name: "API", status: "operational" }]} activeIncidents={0} />
    );
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("API");
  });
  it("outage", () => {
    const { container } = render(
      <StatusDashboardPage overallStatus="major_outage" uptimePct={98}
        services={[{ name: "API", status: "major_outage" }]} activeIncidents={2} />
    );
    expect(container.textContent).toContain("Major System Outage");
    expect(container.textContent).toContain("2 active incidents");
  });
});
