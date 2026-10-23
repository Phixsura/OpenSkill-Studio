import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RetryPolicyConfig } from "@/components/retry-policy-config";

describe("RetryPolicyConfig", () => {
  it("renders policy", () => {
    const { container } = render(
      <RetryPolicyConfig maxRetries={3} backoff="exponential" baseDelayMs={1000}
        maxDelayMs={30000} retryableCodes={[429, 500, 503]} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("Exponential");
    expect(container.textContent).toContain("1000ms");
    expect(container.textContent).toContain("2000ms");
    expect(container.textContent).toContain("429");
    expect(container.textContent).toContain("503");
  });
});
