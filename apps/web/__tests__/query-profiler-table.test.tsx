import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueryProfilerTable } from "@/components/query-profiler-table";

describe("QueryProfilerTable", () => {
  it("renders profiler", () => {
    const { container } = render(
      <QueryProfilerTable totalQueries={100} slowQueries={5} avgTimeMs={25}
        topSlow={[{ query: "SELECT * FROM orders", durationMs: 1500, table: "orders" }]}
        suggestions={[{ query: "SELECT * FROM orders", suggestion: "Add index", impact: "high" }]} />
    );
    expect(container.textContent).toContain("Query Profiler");
    expect(container.textContent).toContain("100 queries");
    expect(container.textContent).toContain("5 slow");
    expect(container.textContent).toContain("1500ms");
    expect(container.textContent).toContain("Add index");
  });
});
