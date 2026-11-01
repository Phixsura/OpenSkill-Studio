import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-benchmark-card";

describe("ConsumerApiBenchmarkCard", () => {
  it("shows benchmarks", () => {
    const results = [{ benchmarkId: "b1", endpoint: "/api/users", rps: 250, avgMs: 45, p95Ms: 120, p99Ms: 200, successful: 98, failed: 2, runAt: "12:00" }];
    const { container } = render(<Card results={results} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("API Benchmarks");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("250 rps");
    expect(container.textContent).toContain("P95: 120ms");
  });
  it("shows empty", () => {
    const { container } = render(<Card results={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No benchmarks run");
  });
});
