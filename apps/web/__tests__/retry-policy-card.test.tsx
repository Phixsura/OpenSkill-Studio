import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RetryPolicyCard from "../src/components/retry-policy-card";

const retryingOp = {
  operation_id: "webhook-delivery-123",
  attempt: 3,
  max_retries: 5,
  strategy: "exponential" as const,
  next_delay_seconds: 8.0,
  exhausted: false,
  first_attempt_at: new Date(Date.now() - 120_000).toISOString(),
  last_attempt_at: new Date(Date.now() - 10_000).toISOString(),
};

const exhaustedOp = {
  operation_id: "email-send-456",
  attempt: 3,
  max_retries: 3,
  strategy: "fixed" as const,
  next_delay_seconds: null,
  exhausted: true,
  first_attempt_at: new Date(Date.now() - 600_000).toISOString(),
  last_attempt_at: new Date(Date.now() - 60_000).toISOString(),
};

const jitterOp = {
  operation_id: "api-call-789",
  attempt: 1,
  max_retries: 10,
  strategy: "exponential_jitter" as const,
  next_delay_seconds: 1.3,
  exhausted: false,
  first_attempt_at: new Date(Date.now() - 5_000).toISOString(),
  last_attempt_at: null,
};

describe("RetryPolicyCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<RetryPolicyCard operations={[retryingOp]} appName="My App" />);
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("My App");
  });

  it("shows retrying count", () => {
    const { container } = render(
      <RetryPolicyCard operations={[retryingOp, jitterOp]} appName="App" />,
    );
    expect(container.textContent).toContain("2 retrying");
  });

  it("shows exhausted count", () => {
    const { container } = render(
      <RetryPolicyCard operations={[retryingOp, exhaustedOp]} appName="App" />,
    );
    expect(container.textContent).toContain("1 exhausted");
  });

  it("renders operation id and strategy", () => {
    const { container } = render(<RetryPolicyCard operations={[retryingOp]} appName="App" />);
    expect(container.textContent).toContain("webhook-delivery-123");
    expect(container.textContent).toContain("Exponential");
  });

  it("shows attempt count bar", () => {
    const { container } = render(<RetryPolicyCard operations={[retryingOp]} appName="App" />);
    expect(container.textContent).toContain("3/5");
  });

  it("shows next delay for retrying operation", () => {
    const { container } = render(<RetryPolicyCard operations={[retryingOp]} appName="App" />);
    expect(container.textContent).toContain("Next in 8.0s");
  });

  it("shows exhausted label", () => {
    const { container } = render(<RetryPolicyCard operations={[exhaustedOp]} appName="App" />);
    expect(container.textContent).toContain("Exhausted");
  });

  it("shows jitter strategy label", () => {
    const { container } = render(<RetryPolicyCard operations={[jitterOp]} appName="App" />);
    expect(container.textContent).toContain("Exp + Jitter");
  });

  it("shows timing info", () => {
    const { container } = render(<RetryPolicyCard operations={[retryingOp]} appName="App" />);
    expect(container.textContent).toContain("Started");
    expect(container.textContent).toContain("Last attempt");
  });

  it("shows empty state", () => {
    const { container } = render(<RetryPolicyCard operations={[]} appName="App" />);
    expect(container.textContent).toContain("No retry operations");
  });
});
