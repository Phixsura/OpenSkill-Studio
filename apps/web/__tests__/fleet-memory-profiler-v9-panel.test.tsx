import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMemoryProfilerV9Panel } from "@/components/fleet-memory-profiler-v9-panel";
describe("FleetMemoryProfilerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetMemoryProfilerV9Panel apps={50} leaks={0} />);
    expect(container.textContent).toContain("Memory Profiler v9");
}); });
