import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-rate-limit-tier-card";

describe("RateLimitTierCard", () => {
  it("shows tiers", () => {
    const endpoints = [{ endpoint: "/users", method: "GET", tiers: [{ tier: "free", rpm: 10, rph: 100, burst: 5 }, { tier: "pro", rpm: 100, rph: 5000, burst: 20 }] }];
    const { container } = render(<Card endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Tiers");
    expect(container.textContent).toContain("GET /users");
    expect(container.textContent).toContain("free: 10/min");
    expect(container.textContent).toContain("pro: 100/min");
  });
  it("shows empty", () => {
    const { container } = render(<Card endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No tier configs");
  });
});
