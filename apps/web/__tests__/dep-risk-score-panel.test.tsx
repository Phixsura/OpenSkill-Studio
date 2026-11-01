import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepRiskScorePanel } from "@/components/dep-risk-score-panel";
describe("DepRiskScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepRiskScorePanel services={[
        { service: "api", score: 85, level: "critical" },
        { service: "static", score: 5, level: "low" },
      ]} />
    );
    expect(container.textContent).toContain("Dependency Risk");
    expect(container.textContent).toContain("2 services scored");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("score: 85");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("low");
  });
});
