import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfBaselinePanel } from "@/components/perf-baseline-panel";
describe("PerfBaselinePanel", () => {
  it("renders", () => {
    const { container } = render(
      <PerfBaselinePanel endpoint="/api/users" baselineP99={100} currentP99={150}
        p99ChangePct={50} verdict="regression" />
    );
    expect(container.textContent).toContain("Perf Baseline");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("regression");
    expect(container.textContent).toContain("+50%");
    expect(container.textContent).toContain("100ms");
    expect(container.textContent).toContain("150ms");
  });
});
