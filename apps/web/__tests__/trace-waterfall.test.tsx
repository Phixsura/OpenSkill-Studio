import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceWaterfall } from "@/components/trace-waterfall";

describe("TraceWaterfall", () => {
  it("renders spans", () => {
    const spans = [
      { span_id: "s1", service: "api", operation: "req", duration_ms: 50, status: "ok" },
      { span_id: "s2", service: "db", operation: "query", duration_ms: 30, status: "ok" },
      { span_id: "s3", service: "webhook", operation: "send", duration_ms: 100, status: "error" },
    ];
    const { container } = render(<TraceWaterfall traceId="abc123" spans={spans} totalDurationMs={180} />);
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("50ms");
  });
});
