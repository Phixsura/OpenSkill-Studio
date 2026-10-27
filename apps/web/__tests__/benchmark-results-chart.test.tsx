import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BenchmarkResultsChart } from "@/components/benchmark-results-chart";

const results = [
  { benchmarkId: "b1", name: "render", meanMs: 12, p95Ms: 18, p99Ms: 25 },
  { benchmarkId: "b2", name: "init", meanMs: 5, p95Ms: 8, p99Ms: 12 },
];

describe("BenchmarkResultsChart", () => {
  it("renders benchmarks", () => {
    const { container } = render(<BenchmarkResultsChart results={results} />);
    expect(container.textContent).toContain("render");
    expect(container.textContent).toContain("mean: 12ms");
    expect(container.textContent).toContain("p95: 18ms");
  });
  it("empty state", () => {
    const { container } = render(<BenchmarkResultsChart results={[]} />);
    expect(container.textContent).toContain("No benchmarks");
  });
});
