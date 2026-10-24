import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PerfTestRunner } from "@/components/perf-test-runner";

describe("PerfTestRunner", () => {
  it("renders", () => {
    const { container } = render(
      <PerfTestRunner passRate={50} passed={1} failed={1} tests={[
        { test: "api-load", targetRps: 1000, actualRps: 980, p99Ms: 200, errorRate: 0.5, passed: true },
        { test: "api-stress", targetRps: 5000, actualRps: 3000, p99Ms: 800, errorRate: 5, passed: false },
      ]} />
    );
    expect(container.textContent).toContain("Perf Tests");
    expect(container.textContent).toContain("50% pass");
    expect(container.textContent).toContain("api-load");
    expect(container.textContent).toContain("980/1000 RPS");
    expect(container.textContent).toContain("api-stress");
  });
});
