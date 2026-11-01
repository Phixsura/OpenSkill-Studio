import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-key-usage-limit-card";

describe("ConsumerApiKeyUsageLimitCard", () => {
  it("shows limits", () => {
    const limits = [{ key_id: "k1", daily_limit: 100, daily_used: 85, monthly_limit: 3000, monthly_used: 2500 }];
    const { container } = render(<Card limits={limits} nearLimitCount={1} appName="App" />);
    expect(container.textContent).toContain("Key Usage Limits");
    expect(container.textContent).toContain("85/100/day");
    expect(container.textContent).toContain("1 near limit");
  });
  it("shows empty", () => {
    const { container } = render(<Card limits={[]} nearLimitCount={0} appName="App" />);
    expect(container.textContent).toContain("No usage limits");
  });
});
