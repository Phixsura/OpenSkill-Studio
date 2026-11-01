import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIOverviewCard from "../src/components/api-developer-api-overview-card";

const overview = {
  total_services: 356, total_endpoints: 1200, total_developers: 500, total_consumers: 2000,
  total_api_calls: 10000000, avg_latency_ms: 85, error_rate: 0.3, uptime_pct: 99.99,
  webhook_destinations: 50, webhook_success_rate: 99.5,
  sdk_versions: 5, documentation_coverage: 95, onboarding_rate: 88, satisfaction_score: 4.6,
};

describe("APIDeveloperAPIOverviewCard", () => {
  it("shows the complete overview", () => {
    const { container } = render(<APIDeveloperAPIOverviewCard overview={overview} appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("API Overview");
    expect(container.textContent).toContain("356");
    expect(container.textContent).toContain("10,000,000");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("4.6/5");
  });
});
