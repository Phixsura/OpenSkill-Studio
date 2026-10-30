import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-webhook-retry-budget-card";

describe("WebhookRetryBudgetCard", () => {
  it("shows budget", () => {
    const { container } = render(<Card consumerId="c1" hourlyUsed={5} hourlyLimit={10} dailyUsed={50} dailyLimit={100} exhausted={false} successRate={0.8} appName="App" />);
    expect(container.textContent).toContain("Retry Budget");
    expect(container.textContent).toContain("5/10");
    expect(container.textContent).toContain("50/100");
    expect(container.textContent).toContain("80%");
  });
  it("shows exhausted", () => {
    const { container } = render(<Card consumerId="c1" hourlyUsed={10} hourlyLimit={10} dailyUsed={100} dailyLimit={100} exhausted={true} successRate={0.2} appName="App" />);
    expect(container.textContent).toContain("EXHAUSTED");
  });
});
