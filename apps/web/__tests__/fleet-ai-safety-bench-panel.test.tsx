import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSafetyBenchPanel } from "@/components/fleet-ai-safety-bench-panel";
describe("FleetAiSafetyBenchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSafetyBenchPanel benchmarks={5} active={5} tests={200000} passRate={99} categories={30} />);
    expect(container.textContent).toContain("Safety Benchmark");
}); });
