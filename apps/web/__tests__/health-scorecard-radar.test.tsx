import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScorecardRadar } from "@/components/health-scorecard-radar";

describe("HealthScorecardRadar", () => {
  it("renders scorecard", () => {
    const dims = { availability: 99.9, performance: 85, security: 90, compliance: 70, dx: 80 };
    const { container } = render(
      <HealthScorecardRadar compositeScore={88} grade="B" dimensions={dims} weakestDimension="compliance"
        recommendations={["Improve compliance"]} />
    );
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("88/100");
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("Improve compliance");
  });
});
