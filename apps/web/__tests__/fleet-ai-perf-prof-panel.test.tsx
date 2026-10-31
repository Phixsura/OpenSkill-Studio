import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPerfProfPanel } from "@/components/fleet-ai-perf-prof-panel";
describe("FleetAiPerfProfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiPerfProfPanel profilers={4} active={4} profiles={50000} bottlenecks={20} optimizations={18} />);
    expect(container.textContent).toContain("Perf Profiler");
}); });
