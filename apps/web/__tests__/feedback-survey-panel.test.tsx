import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeedbackSurveyPanel } from "@/components/feedback-survey-panel";

const results = { q1: { text: "Rate satisfaction", type: "rating", average: 4.2, count: 50 } };
const nps = { nps: 45, responses: 100, promotersPct: 60, detractorsPct: 15 };

describe("FeedbackSurveyPanel", () => {
  it("renders NPS and results", () => {
    const { container } = render(<FeedbackSurveyPanel results={results} nps={nps} />);
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("60% promoters");
    expect(container.textContent).toContain("Rate satisfaction");
    expect(container.textContent).toContain("4.2");
  });
});
