import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-reputation-card";

describe("ConsumerReputationCard", () => {
  it("shows scores", () => {
    const scores = [{ consumer_id: "c1", score: 95, tier: "trusted", violations: 0 }];
    const { container } = render(<Card scores={scores} blockedCount={0} appName="App" />);
    expect(container.textContent).toContain("Consumer Reputation");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("trusted");
  });
  it("shows blocked", () => {
    const { container } = render(<Card scores={[]} blockedCount={2} appName="App" />);
    expect(container.textContent).toContain("2 blocked");
  });
});
