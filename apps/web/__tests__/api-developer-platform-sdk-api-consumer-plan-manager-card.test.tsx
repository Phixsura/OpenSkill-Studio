import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerPlanManagerCard from "../src/components/api-developer-platform-sdk-api-consumer-plan-manager-card";

const consumers = [
  { consumer_id: "acme", plan: "enterprise", limits: { api_calls: -1 } },
  { consumer_id: "beta", plan: "free", limits: { api_calls: 10000 } },
];

describe("Card", () => {
  it("shows plans", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerPlanManagerCard consumers={consumers} planCounts={{ enterprise: 1, free: 1 }} appName="App" />);
    expect(container.textContent).toContain("Consumer Plans");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("enterprise");
    expect(container.textContent).toContain("free: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerPlanManagerCard consumers={[]} planCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No consumers");
  });
});
