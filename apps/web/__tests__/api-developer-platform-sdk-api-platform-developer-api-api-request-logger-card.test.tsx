import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-request-logger-card";

describe("RequestLoggerCard", () => {
  it("shows stats", () => {
    const stats = { total: 50000, errors: 100, avg_duration_ms: 45, total_bytes_in: 5242880, total_bytes_out: 10485760 };
    const { container } = render(<Card stats={stats} errorRate={0.2} appName="App" />);
    expect(container.textContent).toContain("Request Logger");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("5.0 MB");
    expect(container.textContent).toContain("0.2% errors");
  });
  it("shows high error rate", () => {
    const stats = { total: 100, errors: 50, avg_duration_ms: 200, total_bytes_in: 0, total_bytes_out: 0 };
    const { container } = render(<Card stats={stats} errorRate={50} appName="App" />);
    expect(container.textContent).toContain("50% errors");
  });
});
