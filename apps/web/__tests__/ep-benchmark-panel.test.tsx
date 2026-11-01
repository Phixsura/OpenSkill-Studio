import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EpBenchmarkPanel } from "@/components/ep-benchmark-panel";
describe("EpBenchmarkPanel", () => {
  it("renders", () => {
    const { container } = render(
      <EpBenchmarkPanel endpoint="/api/users" samples={1000} avgMs={45}
        p50Ms={40} p95Ms={120} p99Ms={200} throughputRps={500} verdict="ok" />
    );
    expect(container.textContent).toContain("Benchmark: /api/users");
    expect(container.textContent).toContain("ok");
    expect(container.textContent).toContain("500 rps");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("200ms");
  });
});
