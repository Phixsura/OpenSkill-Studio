import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfall } from "@/components/trace-waterfall";

describe("TraceWaterfall", () => {
  it("renders trace", () => {
    const { container } = render(
      <TraceWaterfall traceId="abc123def456" totalDurationMs={45} serviceCount={3} errorCount={1}
        spans={[
          { spanId: "s1", parent: null, service: "gateway", operation: "GET /users", durationMs: 45, status: "ok" },
          { spanId: "s2", parent: "s1", service: "auth", operation: "validate", durationMs: 15, status: "ok" },
          { spanId: "s3", parent: "s1", service: "cache", operation: "get", durationMs: 2, status: "error" },
        ]} />
    );
    expect(container.textContent).toContain("Trace Waterfall");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("gateway");
    expect(container.textContent).toContain("GET /users");
  });
});
