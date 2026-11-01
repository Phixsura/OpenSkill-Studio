import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogPatternViewer } from "@/components/log-pattern-viewer";

describe("LogPatternViewer", () => {
  it("renders", () => {
    const { container } = render(
      <LogPatternViewer totalLines={100} uniquePatterns={15} compressionRatio={15}
        patterns={[
          { pattern: "Request <NUM> completed in <NUM>ms", count: 50, pct: 50 },
          { pattern: "Error connecting to database", count: 20, pct: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Log Patterns");
    expect(container.textContent).toContain("100 lines");
    expect(container.textContent).toContain("15 patterns");
    expect(container.textContent).toContain("Request");
    expect(container.textContent).toContain("50×");
    expect(container.textContent).toContain("Error connecting");
  });
});
