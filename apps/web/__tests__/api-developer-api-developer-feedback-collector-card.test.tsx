import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIDeveloperFeedbackCollectorCard from "../src/components/api-developer-api-developer-feedback-collector-card";

const feedback = [
  { feedback_id: "f1", developer_id: "d1", category: "bug", rating: 4, comment: "Auth is slow", status: "open" },
];

describe("APIDeveloperAPIDeveloperFeedbackCollectorCard", () => {
  it("shows feedback", () => {
    const { container } = render(<APIDeveloperAPIDeveloperFeedbackCollectorCard feedback={feedback} avgRating={4} categoryBreakdown={{ bug: 1 }} appName="App" />);
    expect(container.textContent).toContain("Developer Feedback");
    expect(container.textContent).toContain("1 submissions");
    expect(container.textContent).toContain("bug: 1");
    expect(container.textContent).toContain("Auth is slow");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIDeveloperFeedbackCollectorCard feedback={[]} avgRating={0} categoryBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No feedback yet");
  });
});
