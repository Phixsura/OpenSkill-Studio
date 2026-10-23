import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackSurvey } from "@/components/feedback-survey";

describe("FeedbackSurvey", () => {
  const questions = [
    { id: "q1", text: "Rate this app", type: "rating", required: true, options: null },
    { id: "q2", text: "Comments", type: "text", required: false, options: null },
  ];
  it("renders survey", () => {
    const { container } = render(<FeedbackSurvey title="Feedback" questions={questions} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Feedback");
    expect(container.textContent).toContain("Rate this app");
    expect(container.textContent).toContain("Submit");
  });
});
