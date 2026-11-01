import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSummaryCard from "../src/components/api-developer-platform-summary-card";

const summary = {
  total_developers: 200, active_developers_30d: 150, total_api_calls_30d: 1000000,
  api_error_rate: 0.5, avg_latency_ms: 85, webhook_success_rate: 99.5,
  webhook_destinations: 25, documentation_coverage_pct: 92,
  onboarding_completion_pct: 88, developer_satisfaction: 4.3,
  open_incidents: 0, open_support_tickets: 5,
};

describe("APIDeveloperPlatformSummaryCard", () => {
  it("shows everything", () => {
    const { container } = render(<APIDeveloperPlatformSummaryCard summary={summary} healthGrade="A" appName="App" />);
    expect(container.textContent).toContain("Platform Summary");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("1,000,000");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("4.3/5");
  });
});
