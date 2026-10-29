import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-feedback-collector-card";

describe("FeedbackCollectorCard", () => {
  it("shows feedback", () => {
    const categories = [{ category: "bug", count: 5 }, { category: "feature", count: 3 }];
    const { container } = render(<Card averageRating={4.2} totalFeedback={8} categories={categories} lowRatedCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer Feedback");
    expect(container.textContent).toContain("8 responses");
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("1 low-rated");
    expect(container.textContent).toContain("bug");
  });
  it("shows empty categories", () => {
    const { container } = render(<Card averageRating={0} totalFeedback={0} categories={[]} lowRatedCount={0} appName="App" />);
    expect(container.textContent).toContain("Consumer Feedback");
    expect(container.textContent).toContain("0.0");
  });
});
