import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-plan-comparison-card";

describe("ConsumerPlanComparisonCard", () => {
  it("shows plans", () => {
    const plans = [{ plan_id: "free", name: "Free", price_dollars: "$0", requests: 1000, rps: 10, features: [], support: "community" }, { plan_id: "pro", name: "Pro", price_dollars: "$49.99", requests: 100000, rps: 100, features: ["webhooks"], support: "priority" }];
    const { container } = render(<Card plans={plans} recommendedId="pro" appName="App" />);
    expect(container.textContent).toContain("Plan Comparison");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$49.99/mo");
    expect(container.textContent).toContain("⭐");
  });
  it("shows empty", () => {
    const { container } = render(<Card plans={[]} recommendedId="" appName="App" />);
    expect(container.textContent).toContain("No plans available");
  });
});
