import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FunctionStatsTable } from "@/components/function-stats-table";

const STATS = [
  { function: "sync_data", count: 100, successRate: 98, avgMs: 150, uniqueErrors: 1 },
  { function: "process", count: 50, successRate: 100, avgMs: 30, uniqueErrors: 0 },
];

describe("FunctionStatsTable", () => {
  it("shows functions", () => {
    const { container } = render(<FunctionStatsTable stats={STATS} />);
    expect(container.textContent).toContain("sync_data");
    expect(container.textContent).toContain("process");
  });
  it("shows success rate", () => {
    const { container } = render(<FunctionStatsTable stats={STATS} />);
    expect(container.textContent).toContain("98%");
  });
  it("empty state", () => {
    const { container } = render(<FunctionStatsTable stats={[]} />);
    expect(container.textContent).toContain("No execution");
  });
});
