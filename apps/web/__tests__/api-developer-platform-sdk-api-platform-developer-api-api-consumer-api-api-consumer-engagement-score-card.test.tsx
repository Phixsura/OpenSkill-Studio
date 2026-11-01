import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-engagement-score-card";

describe("ConsumerEngagementScoreCard", () => {
  it("shows scores", () => {
    const scores = [{ consumer_id: "c1", score: 85, level: "power_user" }];
    const { container } = render(<Card scores={scores} dormantCount={0} appName="App" />);
    expect(container.textContent).toContain("Engagement Scores");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("power user");
  });
  it("shows dormant count", () => {
    const { container } = render(<Card scores={[]} dormantCount={5} appName="App" />);
    expect(container.textContent).toContain("5 dormant");
  });
});
