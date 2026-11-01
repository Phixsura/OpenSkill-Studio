import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogAggViewer } from "@/components/log-agg-viewer";

describe("LogAggViewer", () => {
  it("renders", () => {
    const { container } = render(
      <LogAggViewer total={500} errorCount={10} hasErrors={true}
        byLevel={{ info: 400, error: 10, warn: 90 }}
        topSources={[{ source: "api", count: 300 }, { source: "worker", count: 200 }]} />
    );
    expect(container.textContent).toContain("Log Aggregation");
    expect(container.textContent).toContain("500 logs");
    expect(container.textContent).toContain("10 errors");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("300");
  });
});
