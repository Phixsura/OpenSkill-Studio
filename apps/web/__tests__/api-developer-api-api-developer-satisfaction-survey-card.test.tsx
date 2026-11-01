import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperSatisfactionSurveyCard from "../src/components/api-developer-api-api-developer-satisfaction-survey-card";

describe("APIDeveloperAPIApiDeveloperSatisfactionSurveyCard", () => {
  it("shows satisfaction data", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperSatisfactionSurveyCard nps={45} avgSatisfaction={4.2} responseCount={100} recentComments={["Great API!", "Needs better docs"]} appName="App" />);
    expect(container.textContent).toContain("Developer Satisfaction");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("100 responses");
    expect(container.textContent).toContain("4.2/5");
    expect(container.textContent).toContain("Great API!");
  });
});
