import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfallView } from "@/components/trace-waterfall-view";

describe("TraceWaterfallView", () => {
  const roots = [{
    span_id: "s1", service: "gateway", operation: "GET /apps", duration_ms: 100,
    children: [{ span_id: "s2", service: "catalog", operation: "list", duration_ms: 60, children: [] }],
  }];
  it("renders", () => {
    const { container } = render(
      <TraceWaterfallView roots={roots} totalSpans={2} totalDurationMs={100} services={["gateway", "catalog"]} />
    );
    expect(container.textContent).toContain("Trace Waterfall");
    expect(container.textContent).toContain("2 spans");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("catalog");
    expect(container.textContent).toContain("100ms");
  });
});
