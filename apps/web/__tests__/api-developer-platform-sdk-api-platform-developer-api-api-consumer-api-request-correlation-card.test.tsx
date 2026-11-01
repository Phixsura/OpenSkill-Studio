import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-request-correlation-card";

describe("RequestCorrelationCard", () => {
  it("shows traces", () => {
    const traces = [{ trace_id: "abc123def456abcd", span_count: 3, total_duration_ms: 150, has_errors: false }];
    const { container } = render(<Card traces={traces} failedCount={0} appName="App" />);
    expect(container.textContent).toContain("Request Traces");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("150ms");
  });
  it("shows failed count", () => {
    const { container } = render(<Card traces={[]} failedCount={2} appName="App" />);
    expect(container.textContent).toContain("2 failed");
  });
});
