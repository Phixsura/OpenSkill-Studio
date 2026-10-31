import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-rate-limit-override-card";

describe("ConsumerApiRateLimitOverrideCard", () => {
  it("shows overrides", () => {
    const overrides = [{ id: "o1", consumerId: "c1", endpoint: "/api/heavy", multiplier: 3, reason: "Launch event", expiresAt: "2026-06-02" }];
    const { container } = render(<Card overrides={overrides} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Overrides");
    expect(container.textContent).toContain("3x");
    expect(container.textContent).toContain("/api/heavy");
    expect(container.textContent).toContain("Launch event");
  });
  it("shows empty", () => {
    const { container } = render(<Card overrides={[]} appName="App" />);
    expect(container.textContent).toContain("No active overrides");
  });
});
