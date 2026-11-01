import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetProfilerV9Panel } from "@/components/fleet-profiler-v9-panel";
describe("FleetProfilerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetProfilerV9Panel profiles={20} hotspots={5} />);
    expect(container.textContent).toContain("Profiler v9");
}); });
