import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-rate-limit-tier-card";

describe("EndpointRateLimitTierCard", () => {
  it("shows tiers", () => {
    const tiers = [{ id: "basic", name: "Basic", rps: 10, rpm: 100, rph: 1000, burst: 5 }];
    const { container } = render(<Card tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Tiers");
    expect(container.textContent).toContain("Basic");
    expect(container.textContent).toContain("10/s");
    expect(container.textContent).toContain("100/m");
    expect(container.textContent).toContain("+5 burst");
  });
  it("shows empty", () => {
    const { container } = render(<Card tiers={[]} appName="App" />);
    expect(container.textContent).toContain("No rate limit tiers");
  });
});
