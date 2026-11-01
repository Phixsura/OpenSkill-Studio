import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-request-trace-exporter-card";

describe("TraceExporterCard", () => {
  it("shows trace stats", () => {
    const exps = [{ export_id: "e1", format: "otlp", span_count: 500 }];
    const { container } = render(<Card exports={exps} totalSpans={5000} errorSpanCount={50} traceCount={200} appName="App" />);
    expect(container.textContent).toContain("Trace Exporter");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("50 errors");
  });
  it("no error badge when zero", () => {
    const { container } = render(<Card exports={[]} totalSpans={0} errorSpanCount={0} traceCount={0} appName="App" />);
    expect(container.textContent).not.toContain("errors");
  });
});
