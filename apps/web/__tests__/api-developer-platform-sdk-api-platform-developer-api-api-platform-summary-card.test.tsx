import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-platform-summary-card";

describe("PlatformSummaryCard", () => {
  it("shows summary", () => {
    const summary = { total_consumers: 50, active_consumers: 45, total_requests_24h: 100000, error_rate_24h: 1.5, uptime_30d: 99.95, active_incidents: 0, doc_coverage_pct: 90, health_status: "healthy" };
    const { container } = render(<Card summary={summary} issues={[]} appName="OpenSkill" />);
    expect(container.textContent).toContain("Platform Summary");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("45/50");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows issues", () => {
    const summary = { total_consumers: 10, active_consumers: 3, total_requests_24h: 500, error_rate_24h: 15, uptime_30d: 95, active_incidents: 2, doc_coverage_pct: 40, health_status: "critical" };
    const { container } = render(<Card summary={summary} issues={["2 active incidents", "High error rate"]} appName="App" />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("2 active incidents");
  });
});
