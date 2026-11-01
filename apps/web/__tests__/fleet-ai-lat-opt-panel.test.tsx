import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLatOptPanel } from "@/components/fleet-ai-lat-opt-panel";
describe("FleetAiLatOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLatOptPanel services={5} active={5} p50={40} p99={120} optimizations={20} />);
    expect(container.textContent).toContain("Latency Opt");
}); });
