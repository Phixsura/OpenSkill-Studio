import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceViewer } from "@/components/trace-viewer";

const spans = [
  { spanId: "s1", name: "handle_request", parentSpanId: "", status: "ok", durationMs: 50 },
  { spanId: "s2", name: "db_query", parentSpanId: "s1", status: "ok", durationMs: 20 },
  { spanId: "s3", name: "cache_check", parentSpanId: "s1", status: "error", durationMs: 5 },
];

describe("TraceViewer", () => {
  it("renders trace tree", () => {
    const { container } = render(<TraceViewer spans={spans} traceId="abc123def456" />);
    expect(container.textContent).toContain("handle_request");
    expect(container.textContent).toContain("db_query");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("50ms");
  });
});
