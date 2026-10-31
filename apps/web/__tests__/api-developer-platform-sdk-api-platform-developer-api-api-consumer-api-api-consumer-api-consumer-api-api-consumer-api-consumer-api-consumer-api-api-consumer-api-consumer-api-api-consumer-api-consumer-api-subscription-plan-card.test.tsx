import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-consumer-api-subscription-plan-card";

describe("SubscriptionPlanCard", () => {
  it("shows plans with current", () => {
    const plans = [{ id: "free", name: "Free", priceCents: 0, features: [], requestLimit: 1000, rps: 10 }, { id: "pro", name: "Pro", priceCents: 4999, features: ["webhooks"], requestLimit: 100000, rps: 100 }];
    const { container } = render(<Card plans={plans} currentSub={{ planId: "pro", status: "active", trialEndsAt: null }} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Subscription Plans");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$49.99/mo");
    expect(container.textContent).toContain("✓");
  });
  it("shows empty", () => {
    const { container } = render(<Card plans={[]} currentSub={null} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No plans available");
  });
});
