import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCpuProfilerV9Panel } from "@/components/fleet-cpu-profiler-v9-panel";
describe("FleetCpuProfilerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCpuProfilerV9Panel profiles={20} hotspots={3} />);
    expect(container.textContent).toContain("CPU Profiler v9");
}); });
