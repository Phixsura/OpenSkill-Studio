import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperDashboardCard from "../src/components/api-developer-dashboard-card";

const overview = {
  total_api_calls: 50000, active_developers: 25,
  webhook_success_rate: 99.5, active_incidents: 1,
  uptime_pct: 99.95, error_rate: 0.5,
};

describe("APIDeveloperDashboardCard", () => {
  it("renders all metrics", () => {
    const { container } = render(<APIDeveloperDashboardCard overview={overview} appName="App" />);
    expect(container.textContent).toContain("Developer Dashboard");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("99.5%");
  });
});
