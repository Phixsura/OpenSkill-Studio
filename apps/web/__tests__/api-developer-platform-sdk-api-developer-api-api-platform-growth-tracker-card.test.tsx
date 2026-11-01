import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTrackerCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-growth-tracker-card";

const snapshots = [{ period: "2025-01", total_consumers: 200, new_consumers: 30, churned_consumers: 5, net_growth: 25, churn_rate_pct: 2.5, mrr_cents: 500000, growth_healthy: true }];

describe("Card", () => {
  it("shows growth", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTrackerCard snapshots={snapshots} appName="App" />);
    expect(container.textContent).toContain("Platform Growth");
    expect(container.textContent).toContain("+25 net");
    expect(container.textContent).toContain("200 consumers");
    expect(container.textContent).toContain("$5000 MRR");
    expect(container.textContent).toContain("+30 new");
    expect(container.textContent).toContain("2.5% churn");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformGrowthTrackerCard snapshots={[]} appName="App" />);
    expect(container.textContent).toContain("No growth data");
  });
});
