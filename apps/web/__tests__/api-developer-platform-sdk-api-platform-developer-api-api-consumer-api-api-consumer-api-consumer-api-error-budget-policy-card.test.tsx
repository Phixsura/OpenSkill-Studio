import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-error-budget-policy-card";

describe("ConsumerApiErrorBudgetPolicyCard", () => {
  it("shows budget", () => {
    const { container } = render(<Card consumerId="c1" sloTarget={99.9} budgetRemainingPct={75} burnRate={2.5} errorRate={0.05} totalRequests={10000} errorCount={5} alert={false} appName="App" />);
    expect(container.textContent).toContain("Error Budget");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("75%");
    expect(container.textContent).toContain("2.5/h");
  });
  it("shows alert", () => {
    const { container } = render(<Card consumerId="c1" sloTarget={99.9} budgetRemainingPct={0} burnRate={50} errorRate={5} totalRequests={1000} errorCount={50} alert={true} appName="App" />);
    expect(container.textContent).toContain("ALERT");
  });
});
