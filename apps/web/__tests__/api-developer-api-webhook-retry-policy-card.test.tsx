import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookRetryPolicyCard from "../src/components/api-developer-api-webhook-retry-policy-card";

const policies = [
  { policy_id: "default", max_retries: 3, base_delay_seconds: 10, max_delay_seconds: 3600, strategy: "exponential", schedule: [10, 20, 40] },
];

describe("APIDeveloperAPIWebhookRetryPolicyCard", () => {
  it("shows retry policies", () => {
    const { container } = render(<APIDeveloperAPIWebhookRetryPolicyCard policies={policies} appName="App" />);
    expect(container.textContent).toContain("Retry Policies");
    expect(container.textContent).toContain("default");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("3 retries");
    expect(container.textContent).toContain("10s → 20s → 40s");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookRetryPolicyCard policies={[]} appName="App" />);
    expect(container.textContent).toContain("No retry policies");
  });
});
