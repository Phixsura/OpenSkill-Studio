import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngineCard from "../src/components/api-developer-platform-sdk-api-platform-api-api-rate-limit-policy-engine-card";

const policies = [{ policy_id: "p1", name: "Standard Tier", rule_count: 3, consumer_count: 50, enforcement: "enforce" }];

describe("Card", () => {
  it("shows policies", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngineCard policies={policies} activeCount={2} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Policies");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("Standard Tier");
    expect(container.textContent).toContain("3 rules");
    expect(container.textContent).toContain("50 consumers");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiApiRateLimitPolicyEngineCard policies={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No policies");
  });
});
