import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfallPanel } from "@/components/trace-waterfall-panel";
describe("TraceWaterfallPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TraceWaterfallPanel totalMs={200} spanCount={3}
        spans={[
          { service: "gateway", operation: "handle", durationMs: 200, offsetPct: 0, widthPct: 100, depth: 0 },
          { service: "api", operation: "process", durationMs: 150, offsetPct: 5, widthPct: 75, depth: 1 },
          { service: "db", operation: "query", durationMs: 50, offsetPct: 10, widthPct: 25, depth: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Trace Waterfall");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("200ms");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("50ms");
  });
});
