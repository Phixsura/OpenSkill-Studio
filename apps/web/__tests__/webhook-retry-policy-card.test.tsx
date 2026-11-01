import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookRetryPolicyCard from "../src/components/webhook-retry-policy-card";

const schedule = [
  { attempt: 0, delay_seconds: 10, should_retry: true },
  { attempt: 1, delay_seconds: 20, should_retry: true },
  { attempt: 2, delay_seconds: 40, should_retry: true },
  { attempt: 3, delay_seconds: 0, should_retry: false },
];

describe("WebhookRetryPolicyCard", () => {
  it("renders header", () => {
    const { container } = render(
      <WebhookRetryPolicyCard
        policyId="p1"
        strategy="exponential"
        maxRetries={3}
        schedule={schedule}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("p1");
  });

  it("shows strategy badge", () => {
    const { container } = render(
      <WebhookRetryPolicyCard
        policyId="p1"
        strategy="exponential"
        maxRetries={3}
        schedule={schedule}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Exponential");
  });

  it("shows max retries", () => {
    const { container } = render(
      <WebhookRetryPolicyCard
        policyId="p1"
        strategy="exponential"
        maxRetries={3}
        schedule={schedule}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("3 max");
  });

  it("renders attempt delays", () => {
    const { container } = render(
      <WebhookRetryPolicyCard
        policyId="p1"
        strategy="exponential"
        maxRetries={3}
        schedule={schedule}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Attempt 1");
    expect(container.textContent).toContain("10s");
    expect(container.textContent).toContain("40s");
  });

  it("shows exhausted attempt", () => {
    const { container } = render(
      <WebhookRetryPolicyCard
        policyId="p1"
        strategy="exponential"
        maxRetries={3}
        schedule={schedule}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("—");
  });
});
