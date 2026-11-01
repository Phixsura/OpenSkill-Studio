import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBenchSuitePanel } from "@/components/fleet-ai-bench-suite-panel";
describe("FleetAiBenchSuitePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBenchSuitePanel suites={3} active={3} benchmarks={100} models={200} runs={20000} />);
    expect(container.textContent).toContain("Benchmark Suite");
}); });
