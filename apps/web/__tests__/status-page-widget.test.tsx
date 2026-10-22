import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusPageWidget } from "@/components/status-page-widget";

describe("StatusPageWidget", () => {
  it("shows all operational", () => {
    const { container } = render(
      <StatusPageWidget overallStatus="all_operational"
        services={[{ name: "API", status: "operational", uptime_pct: 99.99 }]} />
    );
    expect(container.textContent).toContain("All Systems Operational");
    expect(container.textContent).toContain("API");
  });
  it("shows outage", () => {
    const { container } = render(
      <StatusPageWidget overallStatus="major_outage"
        services={[{ name: "Webhooks", status: "major_outage", uptime_pct: 95 }]} />
    );
    expect(container.textContent).toContain("Major System Outage");
  });
});
