import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdownCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-usage-breakdown-card";

const breakdowns = [{ period: "2025-01", api_calls: 500000, webhook_deliveries: 100000, storage_mb: 500, bandwidth_gb: 50, active_consumers: 200, total_operations: 600000, cost_weighted_score: 750 }];

describe("Card", () => {
  it("shows usage breakdown", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdownCard breakdowns={breakdowns} totalOperations={600000} appName="App" />);
    expect(container.textContent).toContain("Usage Breakdown");
    expect(container.textContent).toContain("600,000 ops");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("API: 500,000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdownCard breakdowns={[]} totalOperations={0} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
