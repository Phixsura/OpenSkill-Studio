import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-latency-budget-card";

describe("EndpointLatencyBudgetCard", () => {
  it("shows budgets", () => {
    const budgets = [{ consumer_id: "c1", endpoint: "/api", method: "GET", budget_ms: 200, compliance_pct: 98, meeting: true }];
    const { container } = render(<Card budgets={budgets} violationCount={0} appName="App" />);
    expect(container.textContent).toContain("Latency Budgets");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("98%");
  });
  it("shows violations", () => {
    const { container } = render(<Card budgets={[]} violationCount={2} appName="App" />);
    expect(container.textContent).toContain("2 violations");
  });
});
