import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProfilerSummaryCard } from "@/components/profiler-summary-card";

describe("ProfilerSummaryCard", () => {
  it("shows stats", () => {
    const { container } = render(<ProfilerSummaryCard total={100} avgMs={50} p95Ms={200} slowestFn="sync" fastestFn="ping" fnCount={3} />);
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("ping");
  });
  it("handles null functions", () => {
    const { container } = render(<ProfilerSummaryCard total={0} avgMs={0} p95Ms={0} slowestFn={null} fastestFn={null} fnCount={0} />);
    expect(container.textContent).toContain("0");
  });
});
