import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TraceViewerPanel } from "@/components/trace-viewer-panel";

const mockTree = {
  spanId: "s1", name: "request", durationMs: 150, status: "ok" as const,
  children: [
    { spanId: "s2", name: "auth", durationMs: 20, status: "ok" as const, children: [] },
    { spanId: "s3", name: "db_query", durationMs: 80, status: "error" as const, children: [
      { spanId: "s4", name: "serialize", durationMs: 10, status: "ok" as const, children: [] },
    ]},
  ],
};
const mockSpans = [
  { spanId: "s1", name: "request", durationMs: 150, status: "ok", parentId: "", eventCount: 0 },
  { spanId: "s2", name: "auth", durationMs: 20, status: "ok", parentId: "s1", eventCount: 1 },
  { spanId: "s3", name: "db_query", durationMs: 80, status: "error", parentId: "s1", eventCount: 0 },
  { spanId: "s4", name: "serialize", durationMs: 10, status: "ok", parentId: "s3", eventCount: 0 },
];

describe("TraceViewerPanel", () => {
  it("renders trace info", () => {
    const { container } = render(
      <TraceViewerPanel tree={mockTree} spans={mockSpans} traceId="tr_abc123" totalDurationMs={150} />
    );
    expect(container.textContent).toContain("tr_abc123");
    expect(container.textContent).toContain("150ms");
    expect(container.textContent).toContain("4 spans");
    expect(container.textContent).toContain("1 errors");
  });

  it("renders tree view with nesting", () => {
    const { container } = render(
      <TraceViewerPanel tree={mockTree} spans={mockSpans} traceId="tr_abc" totalDurationMs={150} />
    );
    expect(container.textContent).toContain("request");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("db_query");
    expect(container.textContent).toContain("serialize");
  });

  it("switches to flat list", () => {
    const { getByText, container } = render(
      <TraceViewerPanel tree={mockTree} spans={mockSpans} traceId="tr_abc" totalDurationMs={150} />
    );
    fireEvent.click(getByText("Flat List"));
    expect(container.textContent).toContain("1 events");
  });
});
