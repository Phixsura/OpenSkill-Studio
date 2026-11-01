import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-overview-card";

describe("ConsumerApiOverviewCard", () => {
  it("shows overview", () => {
    const metrics = [{ name: "Requests", value: 10000, unit: "req/day", trend: "up", changePct: 15 }];
    const { container } = render(<Card consumerId="c1" plan="pro" status="active" healthScore={95} activeKeys={3} activeWebhooks={2} teamMembers={5} metrics={metrics} onboardingComplete={true} appName="App" />);
    expect(container.textContent).toContain("Consumer Overview");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("Requests");
  });
  it("shows onboarding warning", () => {
    const { container } = render(<Card consumerId="c1" plan="free" status="trial" healthScore={50} activeKeys={0} activeWebhooks={0} teamMembers={1} metrics={[]} onboardingComplete={false} appName="App" />);
    expect(container.textContent).toContain("Onboarding incomplete");
  });
});
