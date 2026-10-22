import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceSummaryCard } from "@/components/performance-summary-card";

describe("PerformanceSummaryCard", () => {
  it("shows metrics", () => {
    const { container } = render(<PerformanceSummaryCard count={100} avgMs={150} p50Ms={120} p95Ms={300} p99Ms={500} />);
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("P95");
  });

  it("shows count", () => {
    const { container } = render(<PerformanceSummaryCard count={1000} avgMs={0} p50Ms={0} p95Ms={0} p99Ms={0} />);
    expect(container.textContent).toContain("1,000");
  });

  it("shows empty state", () => {
    const { container } = render(<PerformanceSummaryCard count={0} avgMs={0} p50Ms={0} p95Ms={0} p99Ms={0} />);
    expect(container.textContent).toContain("No execution data");
  });
});
