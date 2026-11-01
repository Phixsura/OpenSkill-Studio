import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperFeedbackSurveyCard from "../src/components/api-developer-feedback-survey-card";

const surveys = [{ survey_id: "s1", title: "API Satisfaction", question_count: 5, response_count: 42 }];

describe("APIDeveloperFeedbackSurveyCard", () => {
  it("shows surveys", () => {
    const { container } = render(<APIDeveloperFeedbackSurveyCard surveys={surveys} appName="App" />);
    expect(container.textContent).toContain("API Satisfaction");
    expect(container.textContent).toContain("42 responses");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperFeedbackSurveyCard surveys={[]} appName="App" />);
    expect(container.textContent).toContain("No surveys");
  });
});
