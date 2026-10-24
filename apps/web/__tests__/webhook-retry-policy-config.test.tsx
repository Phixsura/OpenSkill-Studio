import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookRetryPolicyConfig } from "@/components/webhook-retry-policy-config";

describe("WebhookRetryPolicyConfig", () => {
  const schedule = [
    { attempt: 1, delay_sec: 10, delay_formatted: "10s" },
    { attempt: 2, delay_sec: 20, delay_formatted: "20s" },
    { attempt: 3, delay_sec: 40, delay_formatted: "40s" },
  ];
  it("renders", () => {
    const { container } = render(
      <WebhookRetryPolicyConfig strategy="exponential" maxRetries={3} schedule={schedule}
        totalRetryWindow="0h 1m" onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("10s");
    expect(container.textContent).toContain("20s");
    expect(container.textContent).toContain("40s");
  });
});
