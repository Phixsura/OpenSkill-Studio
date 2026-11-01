import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-endpoint-response-time-budget-card";

describe("EndpointResponseTimeBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ endpoint: "/api", method: "GET", budget_ms: 200, compliance_pct: 98.5, meeting_budget: true, over_budget: 15 }];
    const { container } = render(<Card budgets={budgets} violationCount={0} appName="App" />);
    expect(container.textContent).toContain("Time Budgets");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("98.5%");
  });
  it("shows violations", () => {
    const { container } = render(<Card budgets={[]} violationCount={3} appName="App" />);
    expect(container.textContent).toContain("3 over budget");
  });
});
