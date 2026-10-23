import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetryPolicyConfig } from "@/components/retry-policy-config";

describe("RetryPolicyConfig", () => {
  it("renders policy", () => {
    const { container } = render(
      <RetryPolicyConfig strategy="exponential" maxAttempts={3} totalWaitDisplay="7.0s"
        schedule={[
          { attempt: 1, delayMs: 1000, delayDisplay: "1.0s", capped: false },
          { attempt: 2, delayMs: 2000, delayDisplay: "2.0s", capped: false },
          { attempt: 3, delayMs: 4000, delayDisplay: "4.0s", capped: false },
        ]} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("exponential");
    expect(container.textContent).toContain("3 max");
    expect(container.textContent).toContain("7.0s total");
    expect(container.textContent).toContain("1.0s");
    expect(container.textContent).toContain("4.0s");
  });
});
