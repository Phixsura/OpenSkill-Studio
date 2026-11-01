import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-satisfaction-card";

describe("ConsumerSatisfactionCard", () => {
  it("shows scores", () => {
    const scores = [{ consumer_id: "c1", score: 85, sentiment: "delighted" }];
    const { container } = render(<Card scores={scores} averageScore={85} appName="App" />);
    expect(container.textContent).toContain("Satisfaction");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("delighted");
  });
  it("shows empty", () => {
    const { container } = render(<Card scores={[]} averageScore={0} appName="App" />);
    expect(container.textContent).toContain("No satisfaction data");
  });
});
