import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPICompleteOverviewCard from "../src/components/api-developer-api-complete-overview-card";

const overview = {
  total_services: 388, total_endpoints: 1500, total_developers: 1000,
  api_health_grade: "A", avg_latency_ms: 45, uptime_pct: 99.99,
  webhook_success_rate: 99.8, webhook_destinations: 50,
  developer_satisfaction_nps: 75, onboarding_completion_pct: 92,
  security_score: 98, open_findings: 0,
  documentation_coverage_pct: 95, platform_grade: "A",
};

describe("APIDeveloperAPICompleteOverviewCard", () => {
  it("shows the complete platform overview", () => {
    const { container } = render(<APIDeveloperAPICompleteOverviewCard overview={overview} appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("Complete Platform Overview");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("388");
    expect(container.textContent).toContain("1,500");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("99.8%");
    expect(container.textContent).toContain("75");
    expect(container.textContent).toContain("95%");
  });
});
