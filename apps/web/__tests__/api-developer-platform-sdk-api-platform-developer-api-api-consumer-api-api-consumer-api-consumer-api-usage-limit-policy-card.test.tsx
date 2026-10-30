import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-usage-limit-policy-card";

describe("ConsumerApiUsageLimitPolicyCard", () => {
  it("shows limits", () => {
    const limits = [{ metric: "requests", period: "hour", current: 85, max: 100, resetAt: "13:00" }];
    const { container } = render(<Card limits={limits} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Usage Limits");
    expect(container.textContent).toContain("requests / hour");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("Resets: 13:00");
  });
  it("shows empty", () => {
    const { container } = render(<Card limits={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No usage limits");
  });
});
