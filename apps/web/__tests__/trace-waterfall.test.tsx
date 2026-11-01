import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfall } from "@/components/trace-waterfall";

describe("TraceWaterfall", () => {
  it("renders trace", () => {
    const { container } = render(
      <TraceWaterfall traceId="t1" totalDurationMs={355} criticalSpan="GET /" depth={2}
        spans={[
          { spanId: "s1", operation: "GET /", durationMs: 200, parentId: null },
          { spanId: "s2", operation: "DB query", durationMs: 150, parentId: "s1" },
          { spanId: "s3", operation: "Cache", durationMs: 5, parentId: "s1" },
        ]} />
    );
    expect(container.textContent).toContain("Trace Waterfall");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("355ms");
    expect(container.textContent).toContain("GET /");
    expect(container.textContent).toContain("DB query");
    expect(container.textContent).toContain("bottleneck");
  });
});
