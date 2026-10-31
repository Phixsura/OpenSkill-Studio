import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStartupPrbPanel } from "@/components/fleet-ai-startup-prb-panel";
describe("FleetAiStartupPrbPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStartupPrbPanel probes={4} active={4} services={500} startup={10} failures={0} />);
    expect(container.textContent).toContain("Startup Probe");
}); });
