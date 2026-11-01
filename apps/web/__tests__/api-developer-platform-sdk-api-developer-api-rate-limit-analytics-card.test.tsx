import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalyticsCard from "../src/components/api-developer-platform-sdk-api-developer-api-rate-limit-analytics-card";

const analytics = [{ consumer_id: "acme", throttle_rate: 8.5, peak_rps: 500, total_requests: 100000, needs_upgrade: true }];

describe("Card", () => {
  it("shows rate limit analytics", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalyticsCard analytics={analytics} upgradeCount={1} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Analytics");
    expect(container.textContent).toContain("1 need upgrade");
    expect(container.textContent).toContain("8.5% throttled");
    expect(container.textContent).toContain("500 peak rps");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalyticsCard analytics={[]} upgradeCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate limit data");
  });
});
