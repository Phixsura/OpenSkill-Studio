import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SystemStatusPage } from "@/components/system-status-page";

describe("SystemStatusPage", () => {
  it("renders status", () => {
    const { container } = render(
      <SystemStatusPage overall="All Systems Operational" overallIcon="🟢"
        avgUptimeDisplay="99.97%" lastIncident="None in 30 days"
        services={[
          { name: "API Gateway", status: "operational", uptime: 99.99 },
          { name: "Database", status: "operational", uptime: 99.98 },
        ]} />
    );
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("99.97%");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("None in 30 days");
  });
});
