import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-health-score-card";

describe("ConsumerHealthScoreCard", () => {
  it("shows scores", () => {
    const scores = [{ consumer_id: "c1", score: 95, grade: "A", risk_level: "low" }];
    const { container } = render(<Card scores={scores} atRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("Health Scores");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("A");
  });
  it("shows at risk", () => {
    const { container } = render(<Card scores={[]} atRiskCount={3} appName="App" />);
    expect(container.textContent).toContain("3 at risk");
  });
});
