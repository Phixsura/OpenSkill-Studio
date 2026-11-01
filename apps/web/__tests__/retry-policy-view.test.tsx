import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetryPolicyView } from "@/components/retry-policy-view";

describe("RetryPolicyView", () => {
  const schedule = [
    { attempt: 1, delay_s: 1, cumulative_s: 1 },
    { attempt: 2, delay_s: 2, cumulative_s: 3 },
    { attempt: 3, delay_s: 4, cumulative_s: 7 },
  ];
  it("renders schedule", () => {
    const { container } = render(<RetryPolicyView schedule={schedule} maxAttempts={3} totalWaitS={7} />);
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("3 attempts");
    expect(container.textContent).toContain("7s total");
    expect(container.textContent).toContain("Attempt 1");
    expect(container.textContent).toContain("4s delay");
  });
});
