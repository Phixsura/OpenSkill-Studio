import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-retry-policy-card";

describe("RetryPolicyCard", () => {
  it("shows policies", () => {
    const policies = [{ policy_id: "p1", consumer_id: "c1", strategy: "exponential", max_retries: 5, base_delay_s: 10 }];
    const { container } = render(<Card policies={policies} appName="App" />);
    expect(container.textContent).toContain("Retry Policies");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("10s");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} appName="App" />);
    expect(container.textContent).toContain("No retry policies");
  });
});
