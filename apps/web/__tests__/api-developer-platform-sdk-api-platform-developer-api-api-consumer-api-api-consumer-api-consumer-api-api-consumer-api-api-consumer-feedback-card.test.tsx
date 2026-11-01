import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-feedback-card";

describe("ConsumerApiFeedbackCard", () => {
  it("shows feedback", () => {
    const feedback = [{ id: "f1", rating: 5, category: "api_quality", comment: "Great API!", status: "new", createdAt: "2026-06-01" }];
    const { container } = render(<Card feedback={feedback} averageRating={4.5} totalCount={10} appName="App" />);
    expect(container.textContent).toContain("Consumer Feedback");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("Great API!");
    expect(container.textContent).toContain("4.5/5");
  });
  it("shows empty", () => {
    const { container } = render(<Card feedback={[]} averageRating={0} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No feedback yet");
  });
});
