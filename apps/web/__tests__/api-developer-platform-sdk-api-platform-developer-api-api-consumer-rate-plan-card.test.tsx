import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-rate-plan-card";

describe("ConsumerRatePlanCard", () => {
  it("shows plans", () => {
    const plans = [{ plan_id: "free", name: "Free", requests_per_minute: 60, requests_per_day: 10000, burst_size: 20, consumer_count: 50 }];
    const { container } = render(<Card plans={plans} appName="App" />);
    expect(container.textContent).toContain("Rate Plans");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("60/min");
    expect(container.textContent).toContain("10,000/day");
  });
  it("shows empty", () => {
    const { container } = render(<Card plans={[]} appName="App" />);
    expect(container.textContent).toContain("No rate plans");
  });
});
