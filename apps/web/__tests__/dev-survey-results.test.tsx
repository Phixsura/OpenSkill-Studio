import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DevSurveyResults } from "@/components/dev-survey-results";

describe("DevSurveyResults", () => {
  it("renders results", () => {
    const { container } = render(
      <DevSurveyResults respondents={50} overallSatisfaction={4.2} nps={35}
        categories={{
          docs: { avg: 3.8, responses: 50, satisfied: 30 },
          sdk: { avg: 4.5, responses: 50, satisfied: 45 },
        }} />
    );
    expect(container.textContent).toContain("Developer Satisfaction");
    expect(container.textContent).toContain("50 responses");
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("+35");
    expect(container.textContent).toContain("docs");
    expect(container.textContent).toContain("3.8/5");
    expect(container.textContent).toContain("sdk");
  });
});
