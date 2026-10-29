import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIDocumentationScoreCard from "../src/components/api-developer-api-documentation-score-card";

const score = { endpoint_coverage_pct: 95, example_coverage_pct: 85, error_doc_coverage_pct: 75, overall_score: 85, grade: "B", guide_count: 10 };

describe("APIDeveloperAPIDocumentationScoreCard", () => {
  it("shows doc score", () => {
    const { container } = render(<APIDeveloperAPIDocumentationScoreCard score={score} appName="App" />);
    expect(container.textContent).toContain("Doc Score");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("Endpoints");
    expect(container.textContent).toContain("95%");
  });
});
