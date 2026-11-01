import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiRequestTraceCollectorCard from "../src/components/api-developer-api-api-request-trace-collector-card";

const traces = [{
  trace_id: "abc123", total_duration_ms: 250, has_errors: true,
  spans: [
    { span_id: "s1", operation: "GET /api", service: "gateway", duration_ms: 100, status: "ok" },
    { span_id: "s2", operation: "query", service: "db", duration_ms: 50, status: "error" },
  ],
}];

describe("APIDeveloperAPIApiRequestTraceCollectorCard", () => {
  it("shows traces", () => {
    const { container } = render(<APIDeveloperAPIApiRequestTraceCollectorCard traces={traces} errorCount={1} traceCount={50} appName="App" />);
    expect(container.textContent).toContain("Request Traces");
    expect(container.textContent).toContain("50 traces");
    expect(container.textContent).toContain("1 errors");
    expect(container.textContent).toContain("abc123");
    expect(container.textContent).toContain("2 spans");
    expect(container.textContent).toContain("gateway");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiRequestTraceCollectorCard traces={[]} errorCount={0} traceCount={0} appName="App" />);
    expect(container.textContent).toContain("No traces");
  });
});
