import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsageCard from "../src/components/api-developer-platform-sdk-api-platform-api-consumer-feature-usage-card";

const consumers = [{ consumer_id: "acme", feature_count: 8, total_usage: 50000, top_feature: "webhooks" }];

describe("Card", () => {
  it("shows feature usage", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsageCard consumers={consumers} featurePopularity={{ webhooks: 50, graphql: 10 }} appName="App" />);
    expect(container.textContent).toContain("Feature Usage");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("8 features");
    expect(container.textContent).toContain("webhooks: 50 users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsageCard consumers={[]} featurePopularity={{}} appName="App" />);
    expect(container.textContent).toContain("No usage data");
  });
});
