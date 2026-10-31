import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPerfBenchmarkV9Panel } from "@/components/fleet-perf-benchmark-v9-panel";
describe("FleetPerfBenchmarkV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPerfBenchmarkV9Panel total={50} p99={50} />);
    expect(container.textContent).toContain("Perf Benchmark v9");
}); });
