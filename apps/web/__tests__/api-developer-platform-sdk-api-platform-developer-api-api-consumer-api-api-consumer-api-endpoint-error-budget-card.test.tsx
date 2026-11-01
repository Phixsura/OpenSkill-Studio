import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-error-budget-card";

describe("ConsumerEndpointErrorBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ consumer_id: "c1", endpoint: "/api", method: "GET", slo_pct: 99, budget_used_pct: 45, status: "warning" }];
    const { container } = render(<Card budgets={budgets} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("Error Budgets");
    expect(container.textContent).toContain("45% used");
  });
  it("shows at risk", () => {
    const { container } = render(<Card budgets={[]} atRiskCount={3} appName="App" />);
    expect(container.textContent).toContain("3 at risk");
  });
});
