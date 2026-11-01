import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerformanceProfileTable } from "@/components/performance-profile-table";

const PROFILES = [{ function: "sync", count: 100, avgMs: 50, p50Ms: 40, p95Ms: 120, minMs: 10, maxMs: 200 }];

describe("PerformanceProfileTable", () => {
  it("shows function", () => {
    const { container } = render(<PerformanceProfileTable profiles={PROFILES} />);
    expect(container.textContent).toContain("sync");
    expect(container.textContent).toContain("50ms");
  });
  it("empty state", () => {
    const { container } = render(<PerformanceProfileTable profiles={[]} />);
    expect(container.textContent).toContain("No profiling");
  });
});
