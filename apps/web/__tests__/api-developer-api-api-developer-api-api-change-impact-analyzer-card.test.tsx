import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzerCard from "../src/components/api-developer-api-api-developer-api-api-change-impact-analyzer-card";

const assessments = [
  { change_id: "c1", endpoint: "/api/old", change_type: "endpoint_removed", risk_level: "critical", breaking: true, affected_count: 5, impact_score: 100 },
  { change_id: "c2", endpoint: "/api/users", change_type: "field_added", risk_level: "low", breaking: false, affected_count: 0, impact_score: 10 },
];

describe("APIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzerCard", () => {
  it("shows assessments", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzerCard assessments={assessments} breakingCount={1} highRiskCount={1} appName="App" />);
    expect(container.textContent).toContain("Impact Analyzer");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("endpoint_removed");
    expect(container.textContent).toContain("5 affected");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiChangeImpactAnalyzerCard assessments={[]} breakingCount={0} highRiskCount={0} appName="App" />);
    expect(container.textContent).toContain("No impact assessments");
  });
});
