import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicyCard from "../src/components/api-developer-api-api-developer-api-api-error-budget-policy-card";

const policies = [
  { policy_id: "p1", endpoint: "/api/users", slo_pct: 99.9, remaining_failures: 5, allowed_failures: 10, burn_rate: 0.5, exhausted: false },
  { policy_id: "p2", endpoint: "/api/payments", slo_pct: 99.99, remaining_failures: 0, allowed_failures: 1, burn_rate: 1.0, exhausted: true },
];

describe("Card", () => {
  it("shows policies", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicyCard policies={policies} exhaustedCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Budget Policy");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("5/10 remaining");
    expect(container.textContent).toContain("SLO: 99.9%");
    expect(container.textContent).toContain("burn: 0.5x");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiErrorBudgetPolicyCard policies={[]} exhaustedCount={0} appName="App" />);
    expect(container.textContent).toContain("No budget policies");
  });
});
