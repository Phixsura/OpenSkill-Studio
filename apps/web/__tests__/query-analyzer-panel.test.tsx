import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { QueryAnalyzerPanel } from "@/components/query-analyzer-panel";

describe("QueryAnalyzerPanel", () => {
  it("renders queries", () => {
    const { container } = render(
      <QueryAnalyzerPanel queries={[
        { queryPreview: "SELECT * FROM users", executionMs: 5, rowsScanned: 1, rowsReturned: 1,
          indexUsed: true, efficiencyPct: 100, slow: false, suggestions: [] },
        { queryPreview: "SELECT * FROM logs", executionMs: 500, rowsScanned: 100000, rowsReturned: 100000,
          indexUsed: false, efficiencyPct: 100, slow: true, suggestions: ["Add index"] },
      ]} />
    );
    expect(container.textContent).toContain("Query Analyzer");
    expect(container.textContent).toContain("2 queries");
    expect(container.textContent).toContain("1 slow");
    expect(container.textContent).toContain("SELECT * FROM users");
    expect(container.textContent).toContain("5ms");
    expect(container.textContent).toContain("500ms");
    expect(container.textContent).toContain("Add index");
  });
});
