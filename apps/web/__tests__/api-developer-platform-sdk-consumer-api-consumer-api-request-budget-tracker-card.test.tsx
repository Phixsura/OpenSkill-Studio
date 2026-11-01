import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-request-budget-tracker-card";

describe("RequestBudgetTrackerCard", () => {
  it("shows budget", () => {
    const { container } = render(<Card consumerId="c1" dailyUsed={8000} dailyBudget={10000} dailyPct={80} monthlyUsed={200000} monthlyBudget={300000} monthlyPct={66.7} alertTriggered={true} blocked={false} appName="App" />);
    expect(container.textContent).toContain("Request Budget");
    expect(container.textContent).toContain("ALERT");
    expect(container.textContent).toContain("Daily");
    expect(container.textContent).toContain("Monthly");
  });
  it("shows blocked", () => {
    const { container } = render(<Card consumerId="c1" dailyUsed={15000} dailyBudget={10000} dailyPct={150} monthlyUsed={0} monthlyBudget={300000} monthlyPct={0} alertTriggered={true} blocked={true} appName="App" />);
    expect(container.textContent).toContain("BLOCKED");
  });
});
