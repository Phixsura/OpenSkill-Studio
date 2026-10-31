import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceContextViewer } from "@/components/trace-context-viewer";

describe("TraceContextViewer", () => {
  it("renders context", () => {
    const { container } = render(
      <TraceContextViewer traceId="abc123" spanId="def456" parentId={null}
        operation="GET /api" sampled={true} header="00-abc123-def456-01" childCount={3} />
    );
    expect(container.textContent).toContain("Trace Context");
    expect(container.textContent).toContain("Sampled");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("def456");
    expect(container.textContent).toContain("GET /api");
    expect(container.textContent).toContain("traceparent");
  });
});
