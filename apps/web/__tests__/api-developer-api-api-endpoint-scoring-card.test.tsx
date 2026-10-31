import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiEndpointScoringCard from "../src/components/api-developer-api-api-endpoint-scoring-card";

const scores = [
  { endpoint: "/api/users", composite_score: 95.5, grade: "A", availability_score: 99, latency_score: 95, error_rate_score: 98, documentation_score: 90 },
  { endpoint: "/api/legacy", composite_score: 45, grade: "F", availability_score: 40, latency_score: 30, error_rate_score: 20, documentation_score: 10 },
];

describe("APIDeveloperAPIApiEndpointScoringCard", () => {
  it("shows scores", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointScoringCard scores={scores} failingCount={1} appName="App" />);
    expect(container.textContent).toContain("Endpoint Scores");
    expect(container.textContent).toContain("1 failing");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("95.5");
    expect(container.textContent).toContain("F");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiEndpointScoringCard scores={[]} failingCount={0} appName="App" />);
    expect(container.textContent).toContain("No scores");
  });
});
