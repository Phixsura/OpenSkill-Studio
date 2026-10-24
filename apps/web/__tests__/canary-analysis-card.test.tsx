import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CanaryAnalysisCard } from "@/components/canary-analysis-card";

describe("CanaryAnalysisCard", () => {
  it("renders", () => {
    const { container } = render(
      <CanaryAnalysisCard verdict="fail" action="rollback" reason="Regression in: error_rate"
        metrics={{
          error_rate: { baseline: 1, canary: 5, deltaPct: 400, regression: true, improvement: false },
          p99_ms: { baseline: 200, canary: 205, deltaPct: 2.5, regression: false, improvement: false },
        }} />
    );
    expect(container.textContent).toContain("Canary Analysis");
    expect(container.textContent).toContain("Rollback");
    expect(container.textContent).toContain("error_rate");
    expect(container.textContent).toContain("1 → 5");
    expect(container.textContent).toContain("+400%");
    expect(container.textContent).toContain("Regression in");
  });
});
