import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackSurveyForm } from "@/components/feedback-survey-form";

describe("FeedbackSurveyForm", () => {
  const questions = [
    { id: "q1", text: "How did you find us?", type: "select", options: ["Search", "Social"] },
    { id: "q2", text: "Feedback", type: "text" },
    { id: "q3", text: "Rate", type: "rating", max: 5 },
  ];
  it("renders questions", () => {
    const { container } = render(<FeedbackSurveyForm title="Survey" questions={questions} onSubmit={vi.fn()} onSkip={vi.fn()} />);
    expect(container.textContent).toContain("Survey");
    expect(container.textContent).toContain("How did you find us?");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
