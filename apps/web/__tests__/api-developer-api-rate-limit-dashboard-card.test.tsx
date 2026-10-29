import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIRateLimitDashboardCard from "../src/components/api-developer-api-rate-limit-dashboard-card";

const dash = { total_rules: 20, active_rules: 18, throttled_requests: 500, total_consumers: 50, exhausted_consumers: 2, avg_utilization_pct: 65.0 };

describe("APIDeveloperAPIRateLimitDashboardCard", () => {
  it("shows all metrics", () => {
    const { container } = render(<APIDeveloperAPIRateLimitDashboardCard dashboard={dash} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Dashboard");
    expect(container.textContent).toContain("18/20");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("65%");
  });
});
