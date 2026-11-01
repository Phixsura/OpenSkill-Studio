import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcScorecard } from "@/components/svc-scorecard";

describe("SvcScorecard", () => {
  it("renders", () => {
    const { container } = render(
      <SvcScorecard service="api" avgScore={86} overallGrade="B"
        dimensions={[
          { dimension: "reliability", score: 95, grade: "A" },
          { dimension: "performance", score: 88, grade: "B" },
        ]} />
    );
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("86/100");
    expect(container.textContent).toContain("reliability");
    expect(container.textContent).toContain("95 (A)");
  });
});
