import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalyticsCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-retry-analytics-card";

const analytics = [{ destination: "https://api.example.com", total_retries: 500, retry_success_rate: 85, waste_rate: 10, exhausted_retries: 50 }];

describe("Card", () => {
  it("shows retry analytics", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalyticsCard analytics={analytics} totalRetries={500} appName="App" />);
    expect(container.textContent).toContain("Retry Analytics");
    expect(container.textContent).toContain("500 total retries");
    expect(container.textContent).toContain("85% success");
    expect(container.textContent).toContain("10% waste");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalyticsCard analytics={[]} totalRetries={0} appName="App" />);
    expect(container.textContent).toContain("No retry data");
  });
});
