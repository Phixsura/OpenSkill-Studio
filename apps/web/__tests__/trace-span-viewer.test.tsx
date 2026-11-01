import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceSpanViewer } from "@/components/trace-span-viewer";

describe("TraceSpanViewer", () => {
  it("renders", () => {
    const { container } = render(
      <TraceSpanViewer totalMs={300} services={2}
        spans={[
          { spanId: "s1", service: "api", operation: "handle", durationMs: 200, depth: 0 },
          { spanId: "s2", service: "db", operation: "query", durationMs: 100, depth: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Trace Spans");
    expect(container.textContent).toContain("2 spans");
    expect(container.textContent).toContain("2 services");
    expect(container.textContent).toContain("300ms");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("handle");
    expect(container.textContent).toContain("db");
  });
});
