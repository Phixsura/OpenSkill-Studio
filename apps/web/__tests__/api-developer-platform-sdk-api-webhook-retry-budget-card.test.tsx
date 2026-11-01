import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiWebhookRetryBudgetCard from "../src/components/api-developer-platform-sdk-api-webhook-retry-budget-card";

const budgets = [
  { destination: "https://api.example.com", max_retries_per_hour: 100, retries_used: 80, remaining: 20, usage_pct: 80, exhausted: false },
  { destination: "https://slow.example.com", max_retries_per_hour: 50, retries_used: 50, remaining: 0, usage_pct: 100, exhausted: true },
];

describe("Card", () => {
  it("shows retry budgets", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookRetryBudgetCard budgets={budgets} exhaustedCount={1} appName="App" />);
    expect(container.textContent).toContain("Retry Budget");
    expect(container.textContent).toContain("1 exhausted");
    expect(container.textContent).toContain("20/100 remaining");
    expect(container.textContent).toContain("0/50 remaining");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookRetryBudgetCard budgets={[]} exhaustedCount={0} appName="App" />);
    expect(container.textContent).toContain("No retry budgets");
  });
});
