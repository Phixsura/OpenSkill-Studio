import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfall } from "@/components/trace-waterfall";

describe("TraceWaterfall", () => {
  const spans = [
    { spanId: "s1", parentSpanId: null, operation: "GET /apps", service: "gateway", startedAt: "2026-01-01" },
    { spanId: "s2", parentSpanId: "s1", operation: "findAll", service: "api", startedAt: "2026-01-01" },
  ];
  it("renders spans", () => {
    const { container } = render(
      <TraceWaterfall spans={spans} totalSpans={2} services={["gateway", "api"]} maxDepth={2} />
    );
    expect(container.textContent).toContain("GET /apps");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("2 spans");
    expect(container.textContent).toContain("depth 2");
  });
});
