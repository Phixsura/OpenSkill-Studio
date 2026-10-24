import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthScorecard } from "@/components/health-scorecard";

describe("HealthScorecard", () => {
  it("renders scorecard", () => {
    const { container } = render(
      <HealthScorecard totalScore={93.5} grade="A" targetsMet={4} targetsTotal={5}
        dimensions={[
          { dimension: "reliability", score: 99.95, target: 99.9, weight: 0.3, weighted: 29.99, met: true },
          { dimension: "performance", score: 92, target: 95, weight: 0.25, weighted: 23, met: false },
        ]} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("93.5/100");
    expect(container.textContent).toContain("4/5 targets met");
    expect(container.textContent).toContain("reliability");
    expect(container.textContent).toContain("performance");
  });
});
