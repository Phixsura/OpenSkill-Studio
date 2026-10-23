import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStatusPage } from "@/components/platform-status-page";

describe("PlatformStatusPage", () => {
  const services = [
    { name: "API Gateway", status: "operational" },
    { name: "Database", status: "operational" },
    { name: "Search", status: "degraded" },
  ];
  it("renders", () => {
    const { container } = render(
      <PlatformStatusPage overallStatus="partial_outage" services={services}
        uptime90d={99.5} activeIncidents={0} lastIncidentDaysAgo={5}
        updatedAt="2026-10-23T17:00:00" />
    );
    expect(container.textContent).toContain("Partial System Outage");
    expect(container.textContent).toContain("🟡");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("Search");
  });
});
