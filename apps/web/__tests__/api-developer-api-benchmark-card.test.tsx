import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIBenchmarkCard from "../src/components/api-developer-api-benchmark-card";

const results = [{ benchmark_id: "b1", endpoint: "GET /api/users", rps: 5000, avg_latency_ms: 20, p99_latency_ms: 150, error_rate: 0.1 }];

describe("APIDeveloperAPIBenchmarkCard", () => {
  it("shows benchmarks", () => {
    const { container } = render(<APIDeveloperAPIBenchmarkCard results={results} appName="App" />);
    expect(container.textContent).toContain("API Benchmarks");
    expect(container.textContent).toContain("5,000 rps");
    expect(container.textContent).toContain("20ms avg");
    expect(container.textContent).toContain("p99 150ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIBenchmarkCard results={[]} appName="App" />);
    expect(container.textContent).toContain("No benchmarks");
  });
});
